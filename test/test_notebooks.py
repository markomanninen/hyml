"""Re-execute the notebooks and compare the outputs with the stored ones."""

import copy
from pathlib import Path

import pytest

nbformat = pytest.importorskip("nbformat")
nbclient = pytest.importorskip("nbclient")
pytest.importorskip("ipykernel")

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = ["HyML - Minimal.ipynb", "HyML - XML & (X)HTML generator for Hy.ipynb"]


def outputs(cell):
    """Comparable outputs of a code cell. Printed text may arrive in pieces."""
    stream, results = "", []
    for output in cell.get("outputs", []):
        if output.output_type == "stream":
            stream += output.text
        elif output.output_type in ("execute_result", "display_data"):
            data = output.get("data", {})
            results.append(data.get("text/html", data.get("text/plain")))
        elif output.output_type == "error":
            results.append(f"{output.ename}: {output.evalue}")
    return stream, results


@pytest.mark.parametrize("name", NOTEBOOKS)
def test_notebook_outputs(name):
    stored = nbformat.read(ROOT / name, as_version=4)
    executed = copy.deepcopy(stored)
    nbclient.NotebookClient(executed, timeout=120, kernel_name="python3", allow_errors=True,
                            resources={"metadata": {"path": str(ROOT)}}).execute()
    for i, (old, new) in enumerate(zip(stored.cells, executed.cells)):
        # the environment cell prints Hy and Python versions
        if old.cell_type != "code" or "sys.version" in old.source:
            continue
        assert outputs(new) == outputs(old), f"{name}, cell {i}:\n{old.source}"
