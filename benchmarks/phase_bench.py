"""Measure the safe data mode, for tracking the speed work.

    python benchmarks/phase_bench.py [LABEL]

Prints one markdown row: the 100-row table and the 33-element page, from JSON
lists and from s-expression text, plus the s-expression reader alone and htpy
for comparison. Milliseconds, best of five.
"""

import sys
import timeit
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import hy  # noqa: E402,F401
import hyml  # noqa: E402
import render_bench as b  # noqa: E402
from hyml.sexp import read  # noqa: E402

TABLE = b.table_data(b.ROWS)
PAGE_SEXP = b.pages.static_source


def best(fn):
    number, _ = timeit.Timer(fn).autorange()
    return min(timeit.repeat(fn, number=number, repeat=5)) / number * 1e3


COLUMNS = {
    "table, JSON": lambda: hyml.render_data(TABLE, max_nodes=100000),
    "table, s-expr": lambda: hyml.render_data(b.TABLE_SEXP, max_nodes=100000),
    "table, reader only": lambda: read(b.TABLE_SEXP),
    "page, JSON": lambda: hyml.render_data(b.STATIC_JSON),
    "page, s-expr": lambda: hyml.render_data(PAGE_SEXP),
    "htpy table": lambda: b.table_htpy(b.ROWS),
}

if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    results = {name: best(fn) for name, fn in COLUMNS.items()}
    print("| Step | " + " | ".join(COLUMNS) + " |")
    print("|---|" + "---:|" * len(COLUMNS))
    print(f"| {label} | " + " | ".join(f"{v:.3f}" for v in results.values()) + " |")
