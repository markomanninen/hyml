import asyncio
import json

import pytest

pytest.importorskip("mcp")

from mcp.server.fastmcp.exceptions import ToolError  # noqa: E402

from hyml.mcp_server import mcp, render_html  # noqa: E402


def test_render_sexpression_and_json():
    assert render_html('(ul (li "one") (li "two"))') == "<ul><li>one<li>two</ul>"
    assert render_html('["p", {"class": "x"}, "Hello"]', "xhtml") == '<p class="x">Hello</p>'


def test_problems_are_tool_errors():
    with pytest.raises(ToolError, match="script"):
        render_html('(div (script "x"))')
    with pytest.raises(ToolError, match="not valid JSON"):
        render_html('["p", ')
    with pytest.raises(ToolError, match="dialect must be one of"):
        render_html("(p)", "svg")


def test_save_as(tmp_path, monkeypatch):
    with pytest.raises(ToolError, match="saving is not enabled"):
        render_html("(p)", save_as="a.html")
    monkeypatch.setenv("HYML_OUTPUT_DIR", str(tmp_path))
    assert render_html('(p "x")', save_as="page.html") == "saved page.html (8 bytes)"
    assert (tmp_path / "page.html").read_text() == "<p>x</p>"
    for name in ["../escape.html", "/etc/x.html", ".hidden.html", "page.js"]:
        with pytest.raises(ToolError, match="plain file name"):
            render_html("(p)", save_as=name)


def test_environment_options(monkeypatch):
    monkeypatch.setenv("HYML_ALLOWED_URL_HOSTS", "example.com")
    with pytest.raises(ToolError, match="host that is not allowed"):
        render_html('(img :src "https://evil.example/x.png")')
    monkeypatch.setenv("HYML_UNSAFE", "1")
    monkeypatch.delenv("HYML_ALLOWED_URL_HOSTS")
    assert render_html('(p :style "c" "x")') == "<p style=c>x</p>"


def test_tool_definition_is_small():
    tools = asyncio.run(mcp.list_tools())
    assert [tool.name for tool in tools] == ["render_html"]
    size = len(json.dumps([tool.model_dump(exclude_none=True) for tool in tools]))
    assert size < 1200, size
