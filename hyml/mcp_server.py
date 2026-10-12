# -*- coding: utf-8 -*-
"""MCP server: let agents render HTML from HyML markup data.

    pip install "hyml[mcp]"
    hyml-mcp

One tool, ``render_html``. It takes HyML s-expressions or JSON Hiccup and
renders them with :func:`hyml.render_data`, so nothing is evaluated, text is
escaped and unsafe elements, attributes and URLs are rejected with a list of
problems the agent can fix.

Configuration through environment variables:

HYML_OUTPUT_DIR         directory where ``save_as`` writes pages. Without it
                        pages are returned instead of saved.
HYML_DIALECT            default dialect (html5)
HYML_ALLOWED_TAGS       comma-separated tag allowlist
HYML_ALLOWED_URL_HOSTS  comma-separated hosts that URLs may point to
HYML_EXTERNAL_RESOURCES set to 1 to allow images and media from any host
HYML_UNSAFE             set to 1 to allow scripts, styles and other unsafe markup
"""

import json
import os
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

import hyml

INSTRUCTIONS = """\
Write HTML pages as HyML markup and render them with render_html instead of \
writing HTML by hand. HyML is HTML as s-expressions: the first item is the tag, \
:keywords are attributes, strings are text and nested lists are child elements.
(ul :class "todo" (li "one") (li (a :href "/x" "two")))
renders <ul class=todo><li>one<li><a href=/x>two</a></ul>. \
div#main.note is short for (div :id "main" :class "note"). \
A keyword without a value is a boolean attribute: (input :checked). \
JSON is accepted too: ["ul", {"class": "todo"}, ["li", "one"]]. \
Text is escaped, so put text in strings, never HTML. Scripts, styles, event \
handlers and javascript: URLs are rejected; an error lists every problem with \
its path, fix them all and call again.
"""

mcp = FastMCP("hyml", instructions=INSTRUCTIONS)


def _list(name):
    value = os.environ.get(name, "").strip()
    return [item.strip() for item in value.split(",") if item.strip()] or None


def _options():
    return {
        "allowed_tags": _list("HYML_ALLOWED_TAGS"),
        "allowed_url_hosts": _list("HYML_ALLOWED_URL_HOSTS"),
        "allow_external_resources": os.environ.get("HYML_EXTERNAL_RESOURCES") == "1",
        "safe": os.environ.get("HYML_UNSAFE") != "1",
    }


def _output_path(save_as):
    directory = os.environ.get("HYML_OUTPUT_DIR")
    if not directory:
        raise ToolError("saving is not enabled on this server; leave save_as out to get the HTML back")
    if not re.fullmatch(r"[\w.-]+\.html?", save_as) or save_as.startswith("."):
        raise ToolError("save_as must be a plain file name ending in .html, like page.html")
    return Path(directory) / save_as


@mcp.tool()
def render_html(markup: str, dialect: str = "", save_as: str = "") -> str:
    """Render HTML from HyML markup: s-expressions like (p :class "x" "text") or JSON like ["p", {"class": "x"}, "text"]. dialect: html5 (default), html4, xhtml, xhtml5, xml, html5-min. save_as: file name to save the page to instead of returning it."""
    dialect = dialect or os.environ.get("HYML_DIALECT", "html5")
    source = markup.strip()
    if source.startswith("["):
        try:
            source = json.loads(source)
        except json.JSONDecodeError as e:
            raise ToolError(f"the markup looks like JSON but is not valid JSON: {e}") from None
    try:
        page = hyml.render_data(source, dialect, **_options())
    except hyml.HyMLDataError as e:
        raise ToolError(str(e)) from None
    except ValueError as e:
        raise ToolError(str(e)) from None
    if not save_as:
        return page
    path = _output_path(save_as)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding="utf-8")
    return f"saved {path.name} ({len(page.encode('utf-8'))} bytes)"


def main():
    mcp.run()


if __name__ == "__main__":
    main()
