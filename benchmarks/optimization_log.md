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
