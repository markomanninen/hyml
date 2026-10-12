"""Render the article's tables as HTML pages, with HyML's data mode."""
import sys
from pathlib import Path

import hyml

OUT = Path(sys.argv[1])
CSS = """
body { margin: 0; background: #fff; font: 17px/1.45 -apple-system, "Helvetica Neue", Arial, sans-serif; color: #1f2933; }
figure { margin: 0; padding: 28px 32px; width: 1040px; }
figcaption { font-weight: 600; font-size: 19px; margin-bottom: 14px; }
table { border-collapse: collapse; width: 100%; }
th, td { padding: 8px 12px; border-bottom: 1px solid #e3e8ee; text-align: left; }
th { font-size: 14px; text-transform: uppercase; letter-spacing: .03em; color: #52606d; border-bottom: 2px solid #9aa5b1; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
.icon { font-family: "Material Symbols Rounded"; font-size: 26px; line-height: 1; vertical-align: middle;
        font-variation-settings: "FILL" 1, "wght" 500; }
.blocked .icon { color: #2f7a52; } .passes .icon { color: #c2412a; }
td.blocked, td.passes { text-align: center; } th.mark { text-align: center; }
p.note .icon { font-size: 18px; vertical-align: -4px; }
.legend { margin-right: 22px; color: #3e4c59; }
tr.total td { font-weight: 700; border-top: 2px solid #9aa5b1; border-bottom: none; }
tr.hyml td { background: #fbf6ec; }
p.note { color: #616e7c; font-size: 14px; margin-top: 10px; }
"""


def page(name, body):
    html = hyml.render_data(body, max_nodes=100000)
    (OUT / f"{name}.html").write_text(
        f'<!doctype html><meta charset="utf-8">'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:'
        'opsz,wght,FILL,GRAD@24,500,1,0">'
        f'<style>{CSS}</style>{html}', encoding="utf-8")


ICONS = {"blocked": "verified_user", "passes": "cancel"}


def icon(value):
    return ["span", {"class": "icon", "title": value}, ICONS[value]]


def cell(value):
    return ["td", {"class": value}, icon(value)] if value in ICONS else ["td", value]


attacks = [
    ("<script> element", "bbpbb"), ("Event handler attribute", "bbpbb"), ("javascript: link", "bbpbb"),
    ("Disguised java&#9;script: link", "bbpbb"), ("iframe with srcdoc", "bbpbb"), ("Meta refresh redirect", "bbpbb"),
    ("Image URL leak, no click", "pbpbb"), ("CSS url() leak, no click", "bbpbb"),
    ("Form posting to the attacker", "bbpbb"), ("Link carrying data, needs a click", "ppppb")]
word = {"b": "blocked", "p": "passes"}
page("security", ["figure",
    ["figcaption", "Ten attacks from manipulated agent output, each tool at its default settings"],
    ["table",
     ["thead", ["tr", ["th", "Attack"]] + [["th", {"class": "mark"}, name] for name in
                ["nh3", "justhtml", "htpy", "HyML", "HyML with allowed sites"]]],
     ["tbody"] + [["tr", ["td", name]] + [cell(word[c]) for c in marks] for name, marks in attacks] +
     [["tr", {"class": "total"}, ["td", "Blocked"]] + [["td", {"class": "blocked"}, total]
       for total in ["8 / 10", "9 / 10", "0 / 10", "9 / 10", "10 / 10"]]]],
    ["p", {"class": "note"},
     ["span", {"class": "legend blocked"}, icon("blocked"), " blocked"],
     ["span", {"class": "legend passes"}, icon("passes"), " passes through"],
     "nh3 0.3.7 and justhtml 3.13.0 got the attacks as HTML, htpy 26.5.1 and HyML 1.2 as data."]])

runs = [("Writes HTML itself", "Opus 5.5", "980", "3,529", "$0.032"), ("HyML, JSON", "Opus 5.5", "1,229", "10,250", "$0.051"),
        ("HyML, s-expressions", "Opus 5.5", "1,222", "10,247", "$0.072"),
        ("Writes HTML itself", "Haiku 4.5", "3,234", "7,286", "$0.020"), ("HyML, JSON", "Haiku 4.5", "4,254", "21,043", "$0.036"),
        ("HyML, s-expressions", "Haiku 4.5", "7,152", "29,296", "$0.057")]
page("agents", ["figure",
    ["figcaption", "Claude agents building a product page from data with an injection attack"],
    ["table",
     ["thead", ["tr", ["th", "Way"], ["th", "Model"], ["th", "Attack in page"], ["th", {"class": "num"}, "Tokens written"],
                ["th", {"class": "num"}, "Tokens read"], ["th", {"class": "num"}, "Cost per page"]]],
     ["tbody"] + [["tr", {"class": "hyml"} if way.startswith("HyML") else {}, ["td", way], ["td", model], ["td", "0 of 3"],
                   ["td", {"class": "num"}, out], ["td", {"class": "num"}, inp], ["td", {"class": "num"}, cost]]
                  for way, model, out, inp, cost in runs]],
    ["p", {"class": "note"}, "Claude Code without its built-in tools. Three runs per row, averages per page. Token counts include the model's thinking."]])

speed = [("HyML macro, built once when the program starts", "0", "static pages only"),
         ("HyML safe mode, JSON", "77", "1,071"), ("HyML safe mode, s-expressions", "131", "1,737"),
         ("htpy 26.5.1", "78", "1,073"), ("dominate 2.9.1", "87", "1,296"), ("Jinja2 3.1.6 template", "7", "196"),
         ("Plain Python strings with escaping", "2", "49")]
page("speed", ["figure",
    ["figcaption", "Time to render once, in millionths of a second (smaller is faster)"],
    ["table",
     ["thead", ["tr", ["th", "Implementation"], ["th", {"class": "num"}, "Page, 33 elements"],
                ["th", {"class": "num"}, "Table, 100 rows"]]],
     ["tbody"] + [["tr", {"class": "hyml"} if name.startswith("HyML") else {}, ["td", name],
                   ["td", {"class": "num"}, a], ["td", {"class": "num"}, b]] for name, a, b in speed]],
    ["p", {"class": "note"}, "Best of five on CPython 3.12, Apple Silicon. Every implementation renders the same text."]])
print("ok")
