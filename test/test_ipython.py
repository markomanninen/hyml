import pytest

pytest.importorskip("IPython")

from IPython.core.interactiveshell import InteractiveShell  # noqa: E402


@pytest.fixture(scope="module")
def shell():
    shell = InteractiveShell.instance()
    shell.run_cell("%load_ext hyml.ipython")
    yield shell
    InteractiveShell.clear_instance()


def run(shell, source):
    result = shell.run_cell(source)
    result.raise_error()
    return result.result


def test_cell_magic_returns_last_value(shell):
    assert run(shell, '%%hy\n(require hyml.minimal *)\n(setv greeting "hi")\n(ml (p ~"x"))') == "<p>x</p>"
    # names and macros persist between cells
    assert run(shell, "%%hy\n(ml (b ~(.upper \"y\")))") == "<b>Y</b>"
    assert run(shell, "greeting") == "hi"


def test_line_magic(shell):
    assert run(shell, "%hy (+ 1 2)") == 3


def test_reader_macros_in_same_and_later_cells(shell):
    source = '%%hy\n(require hyml.macros :readers [㎖])\n#㎖(p "a")'
    assert run(shell, source) == "<p>a</p>"
    assert run(shell, '%%hy\n#㎖(p "b")') == "<p>b</p>"
