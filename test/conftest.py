import os
import sys
from pathlib import Path

import pytest

# ML macros render at compile time, and templates are read relative to the
# working directory, so tests run from the repository root. bytecode is
# not written because a cached module would keep markup rendered from old
# template files
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import hy  # noqa: E402,F401


def pytest_collect_file(file_path, parent):
    if file_path.suffix == ".hy" and file_path.name.startswith("test_"):
        return pytest.Module.from_parent(parent, path=file_path)
