"""Token counts for page elements written in five formats.

Extracts the interactive elements (links, buttons, inputs, selects, text
areas) from saved HTML pages, the way a browser agent such as Skyvern
describes a page to its model, writes them as indented JSON, compact JSON,
HTML, HyML JSON and HyML s-expressions, and counts tokens with OpenAI's
tokenizers.

    pip install tiktoken
    python formats.py page1.html page2.html ...

Pages with fewer than ten interactive elements are skipped.
"""

import sys, json, html, itertools, string
from html.parser import HTMLParser
import tiktoken

KEEP = ["type", "name", "placeholder", "value", "aria-label", "href", "title", "alt", "role", "checked", "selected"]
INTERACTIVE = {"a", "button", "input", "select", "textarea"}
VOID = {"input"}

def ids():
    for t in itertools.product(string.ascii_uppercase, repeat=4):
        yield "".join(t)

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.els = []; self.open = []; self.gen = ids()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in INTERACTIVE and not (tag == "input" and a.get("type") == "hidden") and not (tag == "a" and not a.get("href")):
            el = {"id": next(self.gen), "tagName": tag, "attributes": {k: (v or "") for k, v in a.items() if k in KEEP}, "text": ""}
            self.els.append(el)
            if tag not in VOID: self.open.append(el)
    def handle_endtag(self, tag):
        if self.open and self.open[-1]["tagName"] == tag: self.open.pop()
    def handle_data(self, d):
        for el in self.open: el["text"] = (el["text"] + " " + d.strip()).strip()[:100]

def as_json(els, indent=None): return json.dumps(els, indent=indent, ensure_ascii=False)
def as_html(els):
    out = []
    for e in els:
        attrs = "".join(f' {k}="{html.escape(v)}"' for k, v in [("id", e["id"]), *e["attributes"].items()])
        out.append(f"<{e['tagName']}{attrs}>" if e["tagName"] in VOID else f"<{e['tagName']}{attrs}>{html.escape(e['text'])}</{e['tagName']}>")
    return "\n".join(out)
def q(s): return json.dumps(s, ensure_ascii=False)
def as_sexp(els):
    out = []
    for e in els:
        attrs = "".join(f" :{k} {q(v)}" for k, v in [("id", e["id"]), *e["attributes"].items()])
        text = f" {q(e['text'])}" if e["text"] else ""
        out.append(f"({e['tagName']}{attrs}{text})")
    return "\n".join(out)
def as_hyml_json(els):
    return "\n".join(json.dumps([e["tagName"], {"id": e["id"], **e["attributes"]}, *([e["text"]] if e["text"] else [])], ensure_ascii=False) for e in els)

encs = {n: tiktoken.get_encoding(n) for n in ["o200k_base", "cl100k_base"]}
fmts = {"JSON, indented": lambda e: as_json(e, 2), "JSON, compact": as_json, "HTML": as_html, "HyML JSON": as_hyml_json, "HyML s-expr": as_sexp}
totals = {(f, n): 0 for f in fmts for n in encs}
for path in sys.argv[1:]:
    p = P(); p.feed(open(path, errors="replace").read()); els = p.els
    if len(els) < 10: continue
    row = []
    for f, fn in fmts.items():
        text = fn(els)
        for n, enc in encs.items():
            k = len(enc.encode(text)); totals[(f, n)] += k
        row.append(f"{f}: {len(encs['o200k_base'].encode(text))}")
    print(path.split("/")[-1][:40].ljust(40), len(els), "elements |", " | ".join(row))
print()
for n in encs:
    base = totals[("HTML", n)]
    print(n, " | ".join(f"{f} {totals[(f, n)]} ({totals[(f, n)] / base:.2f}x HTML)" for f in fmts))
