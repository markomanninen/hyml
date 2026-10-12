# -*- coding: utf-8 -*-
"""Read HyML markup data: s-expression text as plain lists, never as code.

    >>> read('(p :class "x" "Hello" (b bold))')
    ([['p', {'class': 'x'}, 'Hello', ['b', 'bold']]], [])

Elements become JSON Hiccup lists ``[tag, {attributes}, *children]``, so
s-expressions and JSON share one checker in :mod:`hyml.data`. Only
parentheses, strings, symbols, numbers, :keywords and ; comments are read.
Quote, quasiquote, unquote, reader macros, brackets and braces are reported
as problems with their line and column. Hy's own reader is not used: it is
much slower, and markup data needs none of the language.
"""

import re

# one match per token. whitespace before a token is part of the match, and an
# atom can't start with #, which starts a reader macro
TOKEN = re.compile(r'''
    \s*(?:
      (?P<atom>[^\s()\[\]{}";'`~\#][^\s()\[\]{}";'`~]*)
    | (?P<open>\()
    | (?P<close>\))
    | (?P<string>"(?:[^"\\]|\\.)*")
    | (?P<comment>;[^\n]*)
    | (?P<unterminated>")
    | (?P<code>~@|~|'|`)
    | (?P<macro>\#)
    | (?P<bracket>[\[\]{}])
    )''', re.X | re.S)

ESCAPE = re.compile(r'\\(u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}|x[0-9a-fA-F]{2}|.)', re.S)
SIMPLE = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "0": "\0", "a": "\a",
          "b": "\b", "f": "\f", "v": "\v", "\n": ""}

PREFIX = "the markup is not valid s-expression text: "


class ReadError(Exception):
    pass


# placeholder for a code marker: the form after it is skipped as well
SKIP = object()


def _position(text, index):
    line = text.count("\n", 0, index) + 1
    column = index - (text.rfind("\n", 0, index) + 1) + 1
    return f"line {line}, column {column}"


def _unescape(body, text, index):
    def replace(match):
        code = match.group(1)
        if code in SIMPLE:
            return SIMPLE[code]
        if code[0] in "uUx" and len(code) > 1:
            return chr(int(code[1:], 16))
        raise ReadError(f"{PREFIX}{_position(text, index)}: unknown escape \\{code} in a string")
    return ESCAPE.sub(replace, body)


def _element(items, text, index, problems):
    """[tag, {attributes}, *children] from the items of one ( ... )."""
    if not items:
        problems.append(f"{_position(text, index)}: empty element ()")
        return None
    head, rest = items[0], items[1:]
    if isinstance(head, Keyword):
        problems.append(f"{_position(text, index)}: the tag name must come first, not the attribute :{head}")
        return None
    if not isinstance(head, str):
        problems.append(f"{_position(text, index)}: the tag name must be a symbol or a string")
        return None
    attributes, children, i = {}, [], 0
    while i < len(rest):
        item = rest[i]
        if isinstance(item, Keyword):
            following = rest[i + 1] if i + 1 < len(rest) else None
            # a keyword followed by text is an attribute, otherwise it is boolean
            if isinstance(following, str) and not isinstance(following, Keyword):
                attributes[str(item)] = str(following)
                i += 2
            else:
                attributes[str(item)] = True
                i += 1
        else:
            if item is not None:
                children.append(item)
            i += 1
    return [str(head), attributes, *children] if attributes else [str(head), *children]


class Keyword(str):
    """An :attribute name while reading."""


def read(text):
    """Read markup text into (nodes, problems).

    Syntax errors raise :class:`ReadError`; problems that leave the structure
    readable, like code markers, are collected so that all of them can be
    reported at once.
    """
    stack, problems, top = [], [], []
    target = top
    for match in TOKEN.finditer(text):
        kind = match.lastgroup
        if kind == "atom":
            value = match.group(kind)
            if value[0] == ":":
                if stack:
                    value = Keyword(value[1:])
                else:
                    problems.append(f"{_position(text, match.start(kind))}: attribute {value} is outside an element")
                    continue
        elif kind == "string":
            value = match.group(kind)[1:-1]
            if "\\" in value:
                value = _unescape(value, text, match.start(kind))
        elif kind == "open":
            stack.append((match.start(kind), []))
            target = stack[-1][1]
            continue
        elif kind == "close":
            if not stack:
                raise ReadError(f"{PREFIX}{_position(text, match.start(kind))}: ) without a matching (")
            opened, items = stack.pop()
            target = stack[-1][1] if stack else top
            value = _element([item for item in items if item is not None and item is not SKIP],
                             text, opened, problems)
        elif kind == "comment":
            continue
        elif kind == "unterminated":
            raise ReadError(f"{PREFIX}{_position(text, match.start(kind))}: a string is not closed")
        elif kind == "bracket":
            # reported once, at the opening bracket
            value = match.group(kind)
            if value in "[{":
                problems.append(f"{_position(text, match.start(kind))}: {value} is not markup. "
                                "Use ( ) for elements and \" \" for text")
            continue
        else:
            # code and reader macros: the form after them is skipped as well
            if kind == "code":
                problems.append(f"{_position(text, match.start(kind))}: {match.group(kind)} is code "
                                "(~, ~@, ' and `), which is not allowed in markup data")
            else:
                problems.append(f"{_position(text, match.start(kind))}: # starts a Hy reader macro, "
                                "which is not allowed in markup data")
            target.append(SKIP)
            continue
        if target and target[-1] is SKIP:
            target[-1] = None
        else:
            target.append(value)
    if stack:
        raise ReadError(f"{PREFIX}{_position(text, stack[-1][0])}: this ( is not closed")
    return [node for node in top if node is not None and node is not SKIP], problems
