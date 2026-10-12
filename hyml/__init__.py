# -*- coding: utf-8 -*-
"""HyML - XML / (X)HTML generator for Hy.

The markup macros live in Hy modules::

    (require hyml.minimal *)   ; ml
    (require hyml.macros *)    ; xml, xhtml, xhtml5, html4, html5

From Python, HyML source text can be rendered with :func:`render`.
"""

import hy  # noqa: F401  (makes the .hy modules importable)

from hyml.core import escape  # noqa: E402,F401

__version__ = "1.1.0"

DIALECTS = ("ml", "xml", "xhtml", "xhtml5", "html4", "html5", "html4-min", "html5-min")


def render(source, dialect="ml", variables=None):
    """Render HyML source text to a markup string.

    >>> render('(p :class "x" "Hello")', "html5")
    '<p class=x>Hello</p>'

    ``variables`` is a dictionary available to unquoted code (``~name``)
    in addition to the ``defvar`` / ``deffun`` registry.
    """
    if dialect not in DIALECTS:
        raise ValueError("dialect must be one of: " + ", ".join(DIALECTS))
    forms = list(hy.read_many(source))
    if dialect == "ml":
        from hyml.minimal import parse_mnml
        return "".join(parse_mnml(form, variables) for form in forms)
    from hyml.macros import render as render_forms
    return render_forms(dialect, forms, variables)
