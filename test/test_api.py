import pytest

import hyml


def test_render_dialects():
    assert hyml.render('(p :class "x" "Hello")', "html5") == "<p class=x>Hello</p>"
    assert hyml.render('(p :class "x" "Hello")', "xhtml") == '<p class="x">Hello</p>'
    assert hyml.render('(tag :a "b") (tag)') == '<tag a="b"/><tag/>'


def test_render_variables():
    assert hyml.render("(p ~name)", "html5", {"name": "Ada"}) == "<p>Ada</p>"
    assert hyml.render("(p ~first-name)", variables={"first-name": "Ada"}) == "<p>Ada</p>"


def test_render_rejects_unknown_dialect():
    with pytest.raises(ValueError):
        hyml.render("(p)", "svg")


def test_render_variables_are_kept_apart_between_threads():
    from concurrent.futures import ThreadPoolExecutor

    def job(i):
        return hyml.render("(p ~n ~(do (import time) (time.sleep 0.01) n))", "html5", {"n": i})

    with ThreadPoolExecutor(8) as pool:
        results = list(pool.map(job, range(32)))
    assert results == ["<p>%d%d</p>" % (i, i) for i in range(32)]
