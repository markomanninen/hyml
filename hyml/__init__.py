# -*- coding: utf-8 -*-
"""HyML - XML / (X)HTML generator for Hy.

The markup macros live in Hy modules::

    (require hyml.minimal *)   ; ml
    (require hyml.macros *)    ; xml, xhtml, xhtml5, html4, html5

From Python, HyML source text can be rendered with :func:`render`.
"""

import hy  # noqa: F401  (makes the .hy modules importable)

from hyml.core import HyMLError, escape  # noqa: E402,F401
from hyml.data import HyMLDataError  # noqa: E402,F401

__version__ = "1.3.0"

DIALECTS = ("ml", "xml", "xhtml", "xhtml5", "html4", "html5", "html4-min", "html5-min")


def render_data(source, dialect="html5", **options):
    """Render untrusted markup data without evaluating anything.

    ``source`` is HyML s-expression text or JSON Hiccup data
    (``["p", {"class": "x"}, "Hello"]``). Text and attribute values are
    escaped. In safe mode (the default) elements and attributes that can run
    scripts or load content, URLs with other than http, https, mailto and
    tel schemes, and external URLs that load without a click (images,
    media), are rejected.

    Options: ``allowed_tags``, ``allowed_attributes`` (names or patterns
    like ``"data-*"``), ``allowed_url_hosts``, ``allow_external_resources``,
    ``safe``, ``max_depth`` and ``max_nodes``. Raises :class:`HyMLDataError`
    that lists every problem.

    >>> render_data(["ul", ["li", "one"], ["li", "two"]])
    '<ul><li>one<li>two</ul>'
    """
    from hyml.data import render_data as render
    return render(source, dialect, **options)


def validate_data(source, dialect="html5", **options):
    """List the problems :func:`render_data` would report. Empty means valid."""
    from hyml.data import validate_data as validate
    return validate(source, dialect, **options)


def render(source, dialect="ml", variables=None):
    """Render HyML source text to a markup string.

    The source may contain code (``~``, ``~@``) and it is evaluated, so
    never pass untrusted input here. Use :func:`render_data` for that.

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
