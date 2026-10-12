# -*- coding: utf-8 -*-
"""Safe data mode: check untrusted markup data and render it as HTML.

Markup from users or LLM agents arrives as s-expression text, JSON Hiccup
lists or quoted Hy. It is checked into a light tree of plain tuples, an
element being ``(tag, [(name, value), ...], [children])`` and text an escaped
``str``, and the tree is written out as HTML. Nothing is evaluated.

The tag rules (void elements, optional start and end tags) come from
:mod:`hyml.specs` through :mod:`hyml.macros`, so the macros and the data mode
share them. :mod:`hyml.data` is the public Hy interface to this module.
"""

import fnmatch
import html
import re
from urllib.parse import urlsplit

import hy

from hyml import core, macros
from hyml.core import HyMLError
from hyml.sexp import ReadError
from hyml.sexp import read as read_sexp

DIALECTS = macros.dialects
END_RULES = macros.end_rules
START_RULES = macros.start_rules
BOOLEAN_ATTRIBUTES = macros.boolean_attribute_names
spec = macros.spec
is_void = getattr(macros, hy.mangle("void?"))

# heads that mean code in HyML. they are never tags in data mode
CODE_HEADS = frozenset(["unquote", "unquote-splice", "quote", "quasiquote"])
RESERVED_NAMES = CODE_HEADS | {"."}

# elements that can run scripts, load other documents or change how the page
# is interpreted. meta is allowed, its http-equiv attribute is not. tags and
# attributes listed explicitly in allowed_tags and allowed_attributes are
# allowed even when they are blocked here
BLOCKED_TAGS = frozenset(["script", "style", "iframe", "frame", "frameset", "object", "embed",
                          "applet", "base", "link", "noscript", "param"])

# besides on* event handlers
BLOCKED_ATTRIBUTES = frozenset(["style", "srcdoc", "http-equiv", "ping"])

URL_ATTRIBUTES = frozenset(["href", "src", "action", "formaction", "cite", "poster", "data",
                            "background", "longdesc", "codebase", "manifest", "icon", "xlink:href"])

SAFE_SCHEMES = frozenset(["http", "https", "mailto", "tel"])

# URLs that browsers load without a click. a prompt injected agent can leak
# data in them (GitLab Duo, EchoLeak, CamoLeak), so in safe mode they must be
# relative or point to allowed_url_hosts
RESOURCE_ATTRIBUTES = frozenset(["src", "srcset", "poster", "background", "data", "codebase",
                                 "manifest", "icon", "xlink:href"])

# forms that post to another host are a phishing pattern, so their targets
# need allowed_url_hosts too
FORM_ATTRIBUTES = frozenset(["action", "formaction"])

HTML_TAG_NAME = re.compile(r"[A-Za-z][A-Za-z0-9-]*")
XML_TAG_NAME = re.compile(r"[A-Za-z_][\w.-]*(?::[A-Za-z_][\w.-]*)?")
ATTRIBUTE_NAME = re.compile(r"[A-Za-z_:][\w.:-]*")
UNQUOTED_VALUE = re.compile(r"""[^\s"'=<>`]+""")
CONTROL = re.compile(r"[\x00-\x20]+")
SCHEME = re.compile(r"([A-Za-z][A-Za-z0-9+.-]*):")
SHORTHAND = re.compile(r"([.#])")
MAX_PROBLEMS = 20

MODEL_ATOMS = (hy.models.String, hy.models.Symbol, hy.models.Integer, hy.models.Float)


class HyMLDataError(HyMLError):
    """Markup data was rejected. ``problems`` lists every problem found."""

    def __init__(self, problems):
        self.problems = problems
        super().__init__("%d problem%s in markup data:\n" % (len(problems), "" if len(problems) == 1 else "s")
                         + "\n".join("- " + problem for problem in problems))


def model_text(model):
    """Text of a Hy atom model; numbers lose their model wrapper."""
    if isinstance(model, hy.models.Integer):
        return str(int(model))
    if isinstance(model, hy.models.Float):
        return str(float(model))
    return str(model)


def split_shorthand(name):
    """div#main.note -> ("div", ["main"], ["note"])."""
    parts = SHORTHAND.split(name)
    ids = [parts[i + 1] for i in range(1, len(parts), 2) if parts[i] == "#" and parts[i + 1]]
    classes = [parts[i + 1] for i in range(1, len(parts), 2) if parts[i] == "." and parts[i + 1]]
    return parts[0] or "div", ids, classes


def merge(attributes, name, values):
    """Add shorthand values to an attribute, or put a new attribute first."""
    value = " ".join(values)
    for i, (key, old) in enumerate(attributes):
        if key == name:
            return attributes[:i] + [(key, value if old is True else old + " " + value)] + attributes[i + 1:]
    return [(name, value)] + attributes


class Checker:
    """Checks markup data into the light tree, collecting problems."""

    def __init__(self, dialect, allowed_tags, allowed_attributes, allowed_url_hosts,
                 allow_external_resources, safe, max_depth, max_nodes):
        if dialect not in DIALECTS:
            raise ValueError("dialect must be one of: " + ", ".join(DIALECTS))
        self.dialect = DIALECTS[dialect]
        self.specs = self.dialect["specs"]
        self.allowed_tags = None if allowed_tags is None else frozenset(tag.lower() for tag in allowed_tags)
        self.allowed_attributes = None if allowed_attributes is None else list(allowed_attributes)
        self.allowed_url_hosts = (None if allowed_url_hosts is None
                                  else frozenset(host.lower() for host in allowed_url_hosts))
        self.allow_external_resources = allow_external_resources
        self.safe = safe
        self.max_depth = max_depth
        self.max_nodes = max_nodes
        self.nodes = 0
        self.problems = []

    def problem(self, path, message):
        if len(self.problems) < MAX_PROBLEMS:
            self.problems.append(" > ".join(path) + ": " + message if path else message)

    @staticmethod
    def text(value):
        return [html.escape(value, quote=False)]

    # quoted Hy models

    def from_model(self, node, path, depth):
        if isinstance(node, hy.models.Expression):
            return self.model_element(node, path, depth)
        if isinstance(node, (hy.models.String, hy.models.Symbol)):
            return self.text(str(node))
        if isinstance(node, (hy.models.Integer, hy.models.Float)):
            return self.text(model_text(node))
        if isinstance(node, hy.models.Keyword):
            self.problem(path, "attribute :%s is outside an element" % node.name)
            return []
        self.problem(path, "%s is not markup. Use text or (tag ...)" % type(node).__name__)
        return []

    def model_element(self, node, path, depth):
        head = node[0] if node else None
        if isinstance(head, (hy.models.Symbol, hy.models.String)):
            name = str(head)
        elif core.head_name(head) == ".":
            name = core.dotted_tag(head)
        else:
            name = None
        if not node:
            self.problem(path, "empty element ()")
            return []
        if core.head_name(node) in CODE_HEADS or core.head_name(head) in CODE_HEADS:
            self.problem(path, "~, ~@, ' and ` are code, which is not allowed in markup data")
            return []
        if name is None:
            self.problem(path, "the tag name must be a symbol or a string, not %s" % type(head).__name__)
            return []
        attributes, children, items, i = [], [], list(node[1:]), 0
        while i < len(items):
            item = items[i]
            if isinstance(item, hy.models.Keyword):
                following = items[i + 1] if i + 1 < len(items) else None
                if isinstance(following, MODEL_ATOMS):
                    attributes.append((item.name, model_text(following)))
                    i += 2
                else:
                    # a keyword without a value is a boolean attribute
                    attributes.append((item.name, True))
                    i += 1
            else:
                children.append(item)
                i += 1
        return self.element(name, attributes, children, self.from_model, path, depth)

    # JSON Hiccup data, and s-expression text read into it

    def from_data(self, node, path, depth):
        if isinstance(node, bool):
            self.problem(path, "%s is not markup. Use a string" % node)
            return []
        if isinstance(node, str):
            return self.text(node)
        if isinstance(node, (int, float)):
            return self.text(str(node))
        if node is None:
            return []
        if isinstance(node, (list, tuple)) and node and isinstance(node[0], str):
            return self.data_element(node, path, depth)
        if isinstance(node, (list, tuple)):
            # a list of nodes is a fragment
            return [model for i, child in enumerate(node)
                    for model in self.from_data(child, path + [str(i + 1)], depth)]
        self.problem(path, "%s is not markup. Use a string or [tag, {attributes}, ...children]"
                     % type(node).__name__)
        return []

    def data_element(self, node, path, depth):
        rest = list(node[1:])
        attributes = []
        if rest and isinstance(rest[0], dict):
            for name, value in rest.pop(0).items():
                if value is None or value is False:
                    pass
                elif value is True:
                    attributes.append((str(name), True))
                elif isinstance(value, (str, int, float)) and not isinstance(value, bool):
                    attributes.append((str(name), str(value)))
                elif isinstance(value, (list, tuple)) and all(isinstance(v, str) for v in value):
                    # ["a", "b"] for class lists
                    attributes.append((str(name), " ".join(value)))
                else:
                    self.problem(path + [node[0]],
                                 "attribute %s has a %s value. Use a string, a number, true or a list of strings"
                                 % (name, type(value).__name__))
        return self.element(node[0], attributes, rest, self.from_data, path, depth)

    # checks shared by both formats

    def element(self, name, attributes, children, convert, path, depth):
        # a number at the end of the path is the position of this element
        if path and path[-1].isdigit():
            path = path[:-1] + ["%s[%s]" % (name, path[-1])]
        else:
            path = path + [name]
        html_like = self.specs is not None
        self.nodes += 1
        if self.nodes == self.max_nodes + 1:
            self.problem(path, "more than max_nodes=%d elements" % self.max_nodes)
            return []
        if self.nodes > self.max_nodes:
            return []
        if depth > self.max_depth:
            self.problem(path, "nested deeper than max_depth=%d" % self.max_depth)
            return []
        # div#main.note shorthand in the (x)html dialects
        if html_like:
            tag, ids, classes = split_shorthand(name)
            if ids:
                attributes = merge(attributes, "id", ids)
            if classes:
                attributes = merge(attributes, "class", classes)
        else:
            tag = name
        ok = self.check_tag(tag, path)
        checked = [(attribute, attribute if value is True else html.escape(value, quote=True))
                   for attribute, value in attributes
                   if self.check_attribute(tag, attribute, value, path)]
        content = [node for i, child in enumerate(children)
                   for node in convert(child, path + [str(i + 1)], depth + 1)]
        if ok and html_like and content and is_void(tag, self.specs):
            self.problem(path, "<%s> is a void element and can't have content" % tag)
        return [(tag, checked, content)] if ok else []

    def check_tag(self, tag, path):
        lower = tag.lower()
        pattern = HTML_TAG_NAME if self.specs else XML_TAG_NAME
        if lower in RESERVED_NAMES or not pattern.fullmatch(tag):
            self.problem(path, "%r is not a valid tag name" % tag)
            return False
        if self.specs and spec(tag, self.specs) is None:
            self.problem(path, "<%s> is not an %s element" % (tag, self.dialect["name"]))
            return False
        if self.safe and lower in BLOCKED_TAGS and (self.allowed_tags is None or lower not in self.allowed_tags):
            self.problem(path, "<%s> is not allowed in safe mode, because it can run scripts or load content" % tag)
            return False
        if self.allowed_tags is not None and lower not in self.allowed_tags:
            self.problem(path, "<%s> is not in the allowed tags: %s" % (tag, ", ".join(sorted(self.allowed_tags))))
            return False
        return True

    def check_attribute(self, tag, attribute, value, path):
        lower = attribute.lower()
        if not ATTRIBUTE_NAME.fullmatch(attribute):
            self.problem(path, "%r is not a valid attribute name" % attribute)
            return False
        if (self.safe and (lower.startswith("on") or lower in BLOCKED_ATTRIBUTES)
                and (self.allowed_attributes is None or lower not in self.allowed_attributes)):
            self.problem(path, "attribute %s is not allowed in safe mode" % attribute)
            return False
        if (self.allowed_attributes is not None
                and not any(fnmatch.fnmatchcase(lower, pattern) for pattern in self.allowed_attributes)):
            self.problem(path, "attribute %s is not in the allowed attributes: %s"
                         % (attribute, ", ".join(self.allowed_attributes)))
            return False
        if isinstance(value, str) and (lower in URL_ATTRIBUTES or lower == "srcset"):
            urls = ([candidate.strip().split()[0] for candidate in value.split(",") if candidate.strip()]
                    if lower == "srcset" else [value])
            # every URL is checked, so that every problem is reported
            return all([self.check_url(tag, attribute, url, path) for url in urls])
        return True

    def check_url(self, tag, attribute, url, path):
        # browsers ignore whitespace and control characters inside the scheme
        cleaned = CONTROL.sub("", html.unescape(url))
        scheme = SCHEME.match(cleaned)
        scheme_name = scheme.group(1).lower() if scheme else None
        external = cleaned.startswith("//") or scheme_name in ("http", "https")
        host = (urlsplit(cleaned).hostname or "").lower()
        if self.safe and scheme and scheme_name not in SAFE_SCHEMES:
            self.problem(path, "%s=%r uses the %s: scheme. Use http, https, mailto, tel or a relative URL"
                         % (attribute, url, scheme_name))
            return False
        if self.allowed_url_hosts is not None and external and host not in self.allowed_url_hosts:
            if self.allowed_url_hosts:
                self.problem(path, "%s=%r points to a host that is not allowed: %s"
                             % (attribute, url, ", ".join(sorted(self.allowed_url_hosts))))
            else:
                self.problem(path, "%s=%r points to another site, and no external sites are allowed. "
                             "Use a relative URL" % (attribute, url))
            return False
        if (self.safe and external and self.allowed_url_hosts is None and not self.allow_external_resources
                and (attribute.lower() in RESOURCE_ATTRIBUTES
                     or (tag.lower() == "link" and attribute.lower() == "href"))):
            self.problem(path, "%s=%r loads an external resource without a click, which can leak data. "
                         "Use a relative URL, or allow the host with allowed_url_hosts" % (attribute, url))
            return False
        if self.safe and external and self.allowed_url_hosts is None and attribute.lower() in FORM_ATTRIBUTES:
            self.problem(path, "%s=%r sends form data to another host. "
                         "Use a relative URL, or allow the host with allowed_url_hosts" % (attribute, url))
            return False
        return True


# rendering the checked tree

def sibling_kind(node):
    """What follows an element: a tag name or a kind of text."""
    if isinstance(node, str):
        if node.startswith("<!--"):
            return "#comment"
        return "#whitespace" if node and node[0].isspace() else "#text"
    tag = node[0]
    return "#comment" if tag == "!--" else (re.split(r"[.#]", tag)[0] or "div").lower()


def optional(tag, context, rules=END_RULES):
    rule = rules.get(tag.lower())
    return bool(rule and context and rule(context))


def attributes_html(attributes, minify):
    out = []
    for key, value in attributes:
        if minify and key in BOOLEAN_ATTRIBUTES and key == value:
            out.append(" " + key)
        elif minify and UNQUOTED_VALUE.fullmatch(value):
            out.append(" %s=%s" % (key, value))
        else:
            out.append(' %s="%s"' % (key, value.replace('"', "&quot;")))
    return "".join(out)


def render_element(dialect, node, context):
    tag, attributes, content = node
    html_mode = dialect["html"]
    specs = dialect["specs"]
    start = "<" + tag + attributes_html(attributes, html_mode)
    if specs and is_void(tag, specs):
        return start + (">" if html_mode else "/>")
    body = render_nodes(dialect, content, tag)
    if html_mode:
        omit_start = (dialect["omit-start"] and not attributes
                      and optional(tag, dict(context, **{"first-child": sibling_kind(content[0]) if content else None}),
                                   START_RULES))
        return ("" if omit_start else start + ">") + body + ("" if optional(tag, context) else "</" + tag + ">")
    if not content:
        return start + "/>"
    return start + ">" + body + "</" + tag + ">"


def render_nodes(dialect, items, parent=None):
    """Render siblings. Their neighbours decide which tags may be left out."""
    html_mode = dialect["html"]
    last = len(items) - 1
    after_omitted = None
    parts = []
    for i, item in enumerate(items):
        if isinstance(item, str):
            after_omitted = None
            parts.append(item)
            continue
        context = {"followed-by": sibling_kind(items[i + 1]) if i < last else None,
                   "is-last-child": parent is not None and i == last,
                   "parent": parent.lower() if parent else None,
                   "after-omitted": after_omitted}
        parts.append(render_element(dialect, item, context))
        kind = sibling_kind(item)
        after_omitted = kind if html_mode and optional(kind, context) else None
    return "".join(parts)


# public interface

def check_data(source, dialect="html5", *, allowed_tags=None, allowed_attributes=None,
               allowed_url_hosts=None, allow_external_resources=False, safe=True,
               max_depth=64, max_nodes=10000):
    """Check markup data. Returns (nodes, problems)."""
    checker = Checker(dialect, allowed_tags, allowed_attributes, allowed_url_hosts,
                      allow_external_resources, safe, max_depth, max_nodes)
    if isinstance(source, str):
        # s-expression text is read as plain lists, with HyML's own small reader
        try:
            nodes, read_problems = read_sexp(source)
        except ReadError as e:
            raise HyMLDataError([str(e)]) from None
        checker.problems.extend(read_problems)
        # a single form needs no position in the problem paths
        tree = checker.from_data(nodes[0] if len(nodes) == 1 else nodes, [], 1)
    elif isinstance(source, hy.models.Object):
        # quoted Hy code, like '(p "x")
        tree = checker.from_model(source, [], 1)
    else:
        tree = checker.from_data(source, [], 1)
    return tree, checker.problems[:MAX_PROBLEMS]


def validate_data(source, dialect="html5", **options):
    """List the problems in markup data. An empty list means it renders."""
    try:
        return check_data(source, dialect, **options)[1]
    except HyMLDataError as e:
        return e.problems


def render_data(source, dialect="html5", **options):
    """Render markup data without evaluating anything. Raises HyMLDataError
    listing every problem when the data is rejected."""
    tree, problems = check_data(source, dialect, **options)
    if problems:
        raise HyMLDataError(problems)
    return render_nodes(DIALECTS[dialect], tree)
