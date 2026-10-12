"""Differential test for the safe data mode.

Random markup, valid, broken and malicious, is rendered by the current
implementation (hyml.data) and by the frozen reference copy of the
implementation before the speed work (test/reference_data.hy). Both must give
identical HTML, or identical lists of problems, for every dialect and set of
options, from JSON and from s-expression text.
"""

import random

import pytest

import hyml
import reference_data
from hyml import HyMLDataError

TAGS = ["p", "li", "ul", "ol", "dl", "dt", "dd", "table", "tr", "td", "th", "tbody", "thead",
        "tfoot", "caption", "colgroup", "col", "html", "head", "body", "title", "meta", "div",
        "span", "a", "b", "img", "br", "input", "select", "option", "optgroup", "ruby", "rt",
        "rp", "template", "form", "button", "video", "source", "script", "style", "iframe",
        "link", "blink", "unquote", "quote", "div#main.note", ".box", "p.a.b", "#x", "UL",
        "my-tag", "x y", "frame", "center", "", "note", "h1", "section", "header"]
ATTRIBUTES = ["class", "id", "href", "src", "srcset", "onclick", "OnLoad", "style", "data-x",
              "hidden", "disabled", "checked", "title", "action", "formaction", "poster",
              "http-equiv", "a b", "aria-label", "value", "lang", "rel", "content", "charset"]
VALUES = ["x", "", "a b", "it's", 'say "hi"', "<b>&</b>", "javascript:alert(1)", " java\tscript:x",
          "https://attacker.example/log?d=SECRET", "//cdn.example/a.png", "https://example.com/x",
          "/relative/path", "#top", "mailto:a@b.c", "data:text/html,x", "a.png 1x, javascript:x 2x",
          "refresh", 0, 3.5, True, False, None, ["a", "b"], {"x": 1}]
TEXTS = ["Hello", "", " leading space", "\tTab", "<!-- c", "a<b>&'\"", "line\nbreak", 7, 2.5,
         None, True, "<script>alert(1)</script>", "Ünïcødé ✓"]
OPTIONS = [{}, {"safe": False}, {"allowed_url_hosts": ["example.com"]}, {"allowed_url_hosts": []},
           {"allow_external_resources": True}, {"allowed_tags": ["p", "ul", "li", "a", "link", "b"]},
           {"allowed_attributes": ["href", "class", "data-*", "style"]}, {"max_nodes": 5},
           {"max_depth": 2}]
DIALECTS = ["html5", "html4", "xhtml", "xhtml5", "xml", "html5-min", "html4-min"]


def random_node(rng, depth):
    if depth > 3 or rng.random() < 0.3:
        return rng.choice(TEXTS)
    node = [rng.choice(TAGS)]
    if rng.random() < 0.6:
        node.append({rng.choice(ATTRIBUTES): rng.choice(VALUES) for _ in range(rng.randint(0, 3))})
    for _ in range(rng.randint(0, 4)):
        node.append(random_node(rng, depth + 1))
    if rng.random() < 0.05:
        node.append([random_node(rng, depth + 1), random_node(rng, depth + 1)])  # fragment
    return node


def sexp(node):
    """S-expression text for a JSON node, or None when it has no s-expression form."""
    if isinstance(node, bool) or node is None or isinstance(node, dict):
        return None
    if isinstance(node, (int, float)):
        return str(node)
    if isinstance(node, str):
        return '"' + node.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t") + '"'
    if not node or not isinstance(node[0], str):
        return None
    tag, *rest = node
    if not tag or any(c in tag for c in ' "();'):
        return None
    attrs = rest.pop(0) if rest and isinstance(rest[0], dict) else {}
    parts = [tag]
    for key, value in attrs.items():
        if " " in key or not key:
            return None
        if value is True:
            parts.append(f":{key}")
        elif value is False or value is None:
            continue
        elif isinstance(value, (str, int, float)) and not isinstance(value, bool):
            parts += [f":{key}", sexp(value)]
        else:
            return None
    for child in rest:
        text = sexp(child)
        if text is None:
            return None
        parts.append(text)
    return "(" + " ".join(parts) + ")"


def outcome(render, source, dialect, options):
    try:
        return ("html", render(source, dialect, **options))
    except HyMLDataError as e:
        return ("problems", e.problems)
    except ValueError as e:
        # the reference crashes on XML tag names with dots ("p.a.b"),
        # because it turns every tag into a Hy symbol
        return ("crash", str(e))


def same(new, expected):
    if expected[0] == "crash":
        return new[0] != "crash"
    return new == expected


def cases(seed, count):
    rng = random.Random(seed)
    for _ in range(count):
        node = random_node(rng, 0)
        yield node, rng.choice(DIALECTS), rng.choice(OPTIONS)


@pytest.mark.parametrize("seed", range(10))
def test_json_input_matches_reference(seed):
    for node, dialect, options in cases(seed, 300):
        expected = outcome(reference_data.render_data, node, dialect, options)
        assert same(outcome(hyml.render_data, node, dialect, options), expected), (node, dialect, options)


@pytest.mark.parametrize("seed", range(10))
def test_sexp_input_matches_reference(seed):
    checked = 0
    for node, dialect, options in cases(1000 + seed, 300):
        text = sexp(node)
        if text is None:
            continue
        checked += 1
        expected = outcome(reference_data.render_data, text, dialect, options)
        assert same(outcome(hyml.render_data, text, dialect, options), expected), (text, dialect, options)
    assert checked > 50


SEXP_EDGE_CASES = ['(p ~(os.system "ls") "after")', "(p 'x)", "(p `(b ~x))", '(p #x "y")', "(p [1 2])",
                   "(p (unclosed", '(p "x" "y)', ":class", "(p ())", "(~(+ \"p\" \"\") \"x\")",
                   '(p "a\\"b\\n\\u00e4")', "; comment\n(p x)", "(p :\"attr\")", "(p :a :b c)", "((p) x)",
                   '(p "\\q")', ")", "(p) (b) text 3", '(input :checked :value "a")']


@pytest.mark.parametrize("text", SEXP_EDGE_CASES)
@pytest.mark.parametrize("dialect", ["html5", "xml"])
def test_sexp_edge_cases_match_reference(text, dialect):
    assert same(outcome(hyml.render_data, text, dialect, {}), outcome(reference_data.render_data, text, dialect, {}))
