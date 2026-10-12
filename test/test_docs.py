"""Run the Hy examples of the documentation and compare their outputs.

Every lisp / hylang code block of a document runs in order in one Hy
session, so later blocks see what earlier ones defined. When a block is
followed by "Output:" and a parsed-literal (or xml / html / text) block,
or ends with a "; output: ..." comment, the printed output of
the code block (or the value of its last form, if nothing was printed)
must match it. Blocks after a ".. doctest-skip" comment only illustrate
syntax or show source code, and are not run.
"""

import contextlib
import io
import re
import textwrap
from pathlib import Path

import pytest

import hyml.template
from hyml.core import variables_and_functions
from hyml.session import HySession

ROOT = Path(__file__).resolve().parent.parent
DOCS = ["README.rst", "doc/full.rst", "doc/minimal.rst", "doc/specs.rst", "doc/tests.rst"]
CODE = re.compile(r"\.\. code(?:-block)?:: (?:lisp|hylang)\s*$")
OUTPUT = re.compile(r".*\boutput\b.*:\s*$", re.IGNORECASE)
RESULT = re.compile(r"\.\. (?:parsed-literal::|code(?:-block)?:: (?:xml|html|text)\s*$)")
INLINE = re.compile(r";\s*output:\s*(.+)$")


def directive_body(lines, start):
    """Indented body of the directive at lines[start], and the line after it."""
    body, i = [], start + 1
    while i < len(lines) and (not lines[i].strip() or lines[i].startswith((" ", "\t"))):
        body.append(lines[i])
        i += 1
    body = textwrap.dedent("\n".join(body)).strip("\n").splitlines()
    # directive options like :linenos:
    while body and re.match(r":[\w-]+:", body[0]):
        body.pop(0)
    return "\n".join(body).strip("\n"), i


def examples(path):
    """(line number, code, expected output or None) for each Hy code block to run."""
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        if not CODE.match(lines[i]):
            i += 1
            continue
        lineno = i + 1
        previous = next((line for line in reversed(lines[:i]) if line.strip()), "")
        skip = previous.strip() == ".. doctest-skip"
        code, i = directive_body(lines, i)
        expected = None
        j = i
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and OUTPUT.match(lines[j]):
            j += 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and RESULT.match(lines[j]):
                expected, i = directive_body(lines, j)
        if expected is None and code:
            # (ml (tag)) ; output: <tag/>
            match = INLINE.search(code.splitlines()[-1])
            if match:
                expected = match.group(1)
        if not skip:
            # %%hy marks notebook cells in the docs
            yield lineno, code.removeprefix("%%hy\n"), expected


def normalize(text):
    # the documents show tabs as four spaces
    return "\n".join(line.rstrip() for line in text.expandtabs(4).strip("\n").splitlines())


def shown(value):
    """Text of a value as the docs show it. xml> and friends return HTML objects."""
    if value is None:
        return ""
    return str(getattr(value, "data", value))


@pytest.fixture
def restore_state():
    """The examples define variables, change the template directory and
    write example files to the working directory."""
    registry = dict(variables_and_functions)
    template_dir = hyml.template.template_dir
    files = set(Path.cwd().iterdir())
    yield
    variables_and_functions.clear()
    variables_and_functions.update(registry)
    hyml.template.template_dir = template_dir
    for path in set(Path.cwd().iterdir()) - files:
        if path.is_file():
            path.unlink()


@pytest.mark.parametrize("doc", DOCS)
def test_doc_examples(doc, restore_state):
    session = HySession()
    failures, checked = [], 0
    for lineno, code, expected in examples(ROOT / doc):
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                value = session.run(code, f"{doc}:{lineno}")
        except Exception as e:
            failures.append(f"{doc}:{lineno} raised {type(e).__name__}: {e}")
            continue
        if expected is None:
            continue
        checked += 1
        actual = out.getvalue() or shown(value)
        if normalize(actual) != normalize(expected):
            failures.append(f"{doc}:{lineno}\n--- expected\n{expected}\n--- actual\n{actual}")
    assert not failures, "\n\n".join(failures)
    # specs.rst and tests.rst only need their examples to run
    if doc not in ("doc/specs.rst", "doc/tests.rst"):
        assert checked, "no examples with output found"
