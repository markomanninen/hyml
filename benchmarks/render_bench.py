"""Render the same page and table with HyML and other Python HTML libraries.

    pip install -e ".[mcp]" jinja2 htpy dominate
    python benchmarks/render_bench.py

Prints the best of five timings per render in microseconds. Before timing,
every implementation is checked to produce the same text content.
"""

import html
import importlib.metadata
import platform
import re
import sys
import timeit
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import hy  # noqa: E402,F401
import hyml  # noqa: E402
import pages  # noqa: E402

import dominate.tags as d  # noqa: E402
import htpy as h  # noqa: E402
import jinja2  # noqa: E402

ROWS = [{"name": f"Item <{i}>", "price": round(i * 1.5, 2), "qty": i, "url": f"/items/{i}?a=1&b=2"}
        for i in range(100)]

# static page

STATIC_JSON = ["html", {"lang": "en"},
               ["head", ["meta", {"charset": "utf-8"}], ["title", "HyML benchmark"]],
               ["body",
                ["header", ["h1", "HyML benchmark"],
                 ["nav", ["ul"] + [["li", ["a", {"href": u}, t]] for u, t in
                                   [("/", "Home"), ("/docs", "Docs"), ("/blog", "Blog"), ("/about", "About")]]]],
                ["main", ["article", ["h2", "Markup as data"],
                          ["p", "HyML writes HTML as s-expressions."],
                          ["p", "Text is escaped: <b> & co."],
                          ["ul"] + [["li", w] for w in ["one", "two", "three", "four", "five"]],
                          ["p", ["a", {"href": "https://example.com/?a=1&b=2"}, "A link"]]]],
                ["footer", ["p", "MIT licensed"]]]]

JINJA = jinja2.Environment(autoescape=True)
STATIC_TEMPLATE = JINJA.from_string("""<!doctype html><html lang="en"><head><meta charset="utf-8">\
<title>HyML benchmark</title></head><body><header><h1>HyML benchmark</h1><nav><ul>\
{% for url, text in links %}<li><a href="{{ url }}">{{ text }}</a></li>{% endfor %}</ul></nav></header>\
<main><article><h2>Markup as data</h2><p>HyML writes HTML as s-expressions.</p>\
<p>{{ escaped }}</p><ul>{% for w in words %}<li>{{ w }}</li>{% endfor %}</ul>\
<p><a href="{{ href }}">A link</a></p></article></main><footer><p>MIT licensed</p></footer></body></html>""")
LINKS = [("/", "Home"), ("/docs", "Docs"), ("/blog", "Blog"), ("/about", "About")]
WORDS = ["one", "two", "three", "four", "five"]


def static_jinja():
    return STATIC_TEMPLATE.render(links=LINKS, words=WORDS, escaped="Text is escaped: <b> & co.",
                                  href="https://example.com/?a=1&b=2")


def static_htpy():
    return str(h.html(lang="en")[
        h.head[h.meta(charset="utf-8"), h.title["HyML benchmark"]],
        h.body[
            h.header[h.h1["HyML benchmark"], h.nav[h.ul[(h.li[h.a(href=u)[t]] for u, t in LINKS)]]],
            h.main[h.article[h.h2["Markup as data"], h.p["HyML writes HTML as s-expressions."],
                             h.p["Text is escaped: <b> & co."], h.ul[(h.li[w] for w in WORDS)],
                             h.p[h.a(href="https://example.com/?a=1&b=2")["A link"]]]],
            h.footer[h.p["MIT licensed"]]]])


def static_dominate():
    return d.html(
        d.head(d.meta(charset="utf-8"), d.title("HyML benchmark")),
        d.body(
            d.header(d.h1("HyML benchmark"), d.nav(d.ul([d.li(d.a(t, href=u)) for u, t in LINKS]))),
            d.main(d.article(d.h2("Markup as data"), d.p("HyML writes HTML as s-expressions."),
                             d.p("Text is escaped: <b> & co."), d.ul([d.li(w) for w in WORDS]),
                             d.p(d.a("A link", href="https://example.com/?a=1&b=2")))),
            d.footer(d.p("MIT licensed"))),
        lang="en").render(pretty=False)


STATIC = {
    "HyML html5 macro (compiled)": pages.static_page,
    "HyML render_data, JSON": lambda: hyml.render_data(STATIC_JSON),
    "HyML render_data, s-expression text": lambda: hyml.render_data(pages.static_source),
    "HyML render, s-expression text": lambda: hyml.render(pages.static_source.replace(
        "<b> & co.", "&lt;b&gt; &amp; co.").replace("a=1&b=2", "a=1&amp;b=2"), "html5"),
    "Jinja2 template": static_jinja,
    "htpy": static_htpy,
    "dominate": static_dominate,
}

# table from data

TABLE_TEMPLATE = JINJA.from_string("""<table><thead><tr><th>Name</th><th>Price</th><th>Qty</th></tr></thead>\
<tbody>{% for r in rows %}<tr><td><a href="{{ r.url }}">{{ r.name }}</a></td><td>{{ r.price }}</td>\
<td>{{ r.qty }}</td></tr>{% endfor %}</tbody></table>""")


def table_data(rows):
    return ["table", ["thead", ["tr", ["th", "Name"], ["th", "Price"], ["th", "Qty"]]],
            ["tbody"] + [["tr", ["td", ["a", {"href": r["url"]}, r["name"]]], ["td", r["price"]], ["td", r["qty"]]]
                         for r in rows]]


def table_htpy(rows):
    return str(h.table[h.thead[h.tr[h.th["Name"], h.th["Price"], h.th["Qty"]]],
                       h.tbody[(h.tr[h.td[h.a(href=r["url"])[r["name"]]], h.td[str(r["price"])], h.td[str(r["qty"])]]
                                for r in rows)]])


def table_dominate(rows):
    return d.table(d.thead(d.tr(d.th("Name"), d.th("Price"), d.th("Qty"))),
                   d.tbody([d.tr(d.td(d.a(r["name"], href=r["url"])), d.td(r["price"]), d.td(r["qty"]))
                            for r in rows])).render(pretty=False)


def table_fstring(rows):
    e = html.escape
    body = "".join(f'<tr><td><a href="{e(r["url"])}">{e(r["name"])}</a></td><td>{r["price"]}</td><td>{r["qty"]}</td></tr>'
                   for r in rows)
    return f"<table><thead><tr><th>Name</th><th>Price</th><th>Qty</th></tr></thead><tbody>{body}</tbody></table>"


TABLE = {
    "HyML render_data, JSON built in Python": lambda: hyml.render_data(table_data(ROWS), max_nodes=100000),
    "HyML render with ~@ code (evaluated per call)": lambda: hyml.render(pages.table_source, "html5", {"rows": ROWS}),
    "Jinja2 template": lambda: TABLE_TEMPLATE.render(rows=ROWS),
    "htpy": lambda: table_htpy(ROWS),
    "dominate": lambda: table_dominate(ROWS),
    "f-strings + html.escape": lambda: table_fstring(ROWS),
}


def text(markup):
    """Text content, for checking that the implementations agree."""
    return html.unescape(re.sub(r"<[^>]*>", "", markup)).strip()


def best_us(fn, repeat=5):
    number, _ = timeit.Timer(fn).autorange()
    return min(timeit.repeat(fn, number=number, repeat=repeat)) / number * 1e6


def run(title, cases):
    texts = {name: text(fn()) for name, fn in cases.items()}
    expected = next(iter(texts.values()))
    for name, value in texts.items():
        assert value == expected, f"{title}: {name} renders different text"
    print(f"\n{title}\n")
    print("| Implementation | µs per render | Output bytes |")
    print("|---|---:|---:|")
    for name, fn in cases.items():
        print(f"| {name} | {best_us(fn):,.1f} | {len(fn().encode()):,} |")


if __name__ == "__main__":
    versions = {p: importlib.metadata.version(p) for p in ["hy", "jinja2", "htpy", "dominate"]}
    print(f"Python {platform.python_version()} on {platform.machine()}, hyml {hyml.__version__}, "
          + ", ".join(f"{k} {v}" for k, v in versions.items()))
    run("Static page (33 elements)", STATIC)
    run("Table with 100 rows from data", TABLE)
