# Speed work on the safe data mode

Started 2026-10-12 from HyML 1.2.1. The goal was to bring `render_data` close to
htpy without changing any output. Each step was measured with
`benchmarks/phase_bench.py` (milliseconds, best of five, CPython 3.12 on Apple
Silicon) and checked with `test/test_differential.py`, which renders about
6,000 random markup trees, valid, broken and malicious, with both the frozen
1.2.1 implementation (`test/reference_data.hy`) and the current one, and
requires identical HTML or identical problem lists.

## Plan and expectations

| Step | Change | Expected |
|---|---|---|
| 1 | Check into a light tree of plain tuples and write HTML from it, in plain Python, instead of building Hy models and walking them with the macro renderer (planned steps 1 and 4 together) | table from JSON 2.9 → about 1.3 ms |
| 2 | Faster s-expression reader: positions only for errors, fast path for strings without escapes | reader 1.1 → about 0.5 ms |
| 3 | Remember per-tag and per-attribute decisions | 10-20 % |

## Results

| Step | table, JSON | table, s-expr | table, reader only | page, JSON | page, s-expr | htpy table |
|---|---:|---:|---:|---:|---:|---:|
| 0. baseline (1.2.1) | 2.907 | 3.982 | 1.123 | 0.187 | 0.273 | 1.051 |
| 1. light tree in Python | 1.592 | 2.702 | 1.135 | 0.097 | 0.183 | 1.052 |
| 2. reader, one match per token | 1.573 | 2.201 | 0.683 | 0.098 | 0.148 | 1.062 |
| 2b. filter children only when needed (reverted) | 1.582 | 2.221 | 0.670 | 0.099 | 0.147 | 1.060 |
| 3. per-tag verdicts and node info | 1.020 | 1.720 | 0.674 | 0.077 | 0.132 | 1.039 |
| **Total speedup** | **2.9×** | **2.3×** | **1.7×** | **2.4×** | **2.1×** | |

## Notes

**Step 0.** Freezing the 1.2.1 implementation and running the differential
test found a crash in 1.2.1: a JSON tag name with a dot in the `xml` dialect,
such as `"p.a.b"`, passed the name check, and then Hy refused to make a symbol
of it (`ValueError: Syntactically illegal symbol`). The new implementation
builds no Hy symbols, so the test only requires that it does not crash there.

**Step 1.** Expected 1.3 ms, measured 1.59 ms for the table: 1.8× faster
instead of the hoped 2.2×. The static page became 1.9× faster. All
differential cases match the reference. The remaining time is spread over
the checker (`element`, `from_data`), the renderer (`render_nodes`) and
per-element lookups (`optional`, `void?`, `str.lower`, `split_shorthand`),
which is what step 3 targets.

**Step 2.** The plan assumed that the reader computed line and column numbers
for every token. Profiling showed it already did that only for errors, so the
real costs were elsewhere: one regex match for every run of whitespace (about
1,000 of the 3,000 matches for the table), a function call for every item
added to a list, and an escape-processing regex for every string. Each token is
now one match with its leading whitespace, the adding is inlined, and escapes
are processed only in strings with a backslash. Expected 0.5 ms, measured
0.68 ms: 1.7× faster instead of 2.2×. Filtering a closed element's children
only when a code marker left a placeholder (2b) gained under 2 %, within the
noise, and was reverted.

**Step 3.** Expected 10-20 %, measured 35 % for the table. Within one call,
the checker remembers each tag's and each attribute name's verdict (a problem
message or none), and still reports a problem at every place it occurs. Each
element node carries its sibling kind, void flag and tag rules, so the
renderer no longer lowercases names or looks rules up, and the shorthand
regex runs only for names with `.` or `#`. The table from JSON, 1.02 ms, is now
on par with htpy's 1.04 ms.

## Outcome

| | Before | After | Expected |
|---|---:|---:|---:|
| Table from JSON | 2.91 ms | 1.02 ms | 1.0-1.3 ms |
| Table from s-expression text | 3.98 ms | 1.72 ms | 1.5-1.8 ms |

Both ended inside the expected range, although steps 1 and 2 each fell short
of their own estimate and step 3 made up for it. The differential test passed
after every step. Jinja2 stays about 5× faster from JSON, because it compiles
each template into a Python function once. That gap belongs to the design, and
closing it is not planned.
