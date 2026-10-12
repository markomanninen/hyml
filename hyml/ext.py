# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Copyright (c) Marko Manninen <elonmedia@gmail.com>, 2017-2026
# ---------------------------------------------------------
#
# Babel message extractor for Hy and HyML files.
#
# The package registers it as an entry point:
#
#   [project.entry-points."babel.extractors"]
#   hyml = "hyml.ext:babel_extract"
#
# and then in babel.cfg:
#
#   [hyml: **.hyml]
#   [hyml: **.hy]
#
# -----------------------------------------------------------------------
# LOCALIZATION ROUTINE
# -----------------------------------------------------------------------
# 1. extract messages:
# pybabel extract -F babel.cfg -o messages.pot .
# 2. initialize language file:
# pybabel init -i messages.pot -d translations -l en
# 3. make changes to the language file (manually or via third party app)
# 4. update translation messages:
# pybabel update -i messages.pot -d translations
# 5. compile translations
# pybabel compile -d translations
# -----------------------------------------------------------------------

import hy
from hy.models import Expression, String, Symbol
from hy.reader import HyReader

# accepted gettext / babel keywords
KEYWORDS = ("_", "gettext", "ngettext", "N_", "lgettext", "lngettext", "lazy_gettext")


def _reader():
    """Hy reader that knows the HyML reader macros.

    #i"message" is the shorthand for (_ "message") from hyml.minimal, and
    #㎖ only renders markup, so its form is read as such.
    """
    reader = HyReader()
    reader.reader_macros["i"] = lambda r, key: Expression([Symbol("_"), r.parse_one_form()])
    reader.reader_macros["㎖"] = lambda r, key: r.parse_one_form()
    return reader


def _messages(model, keywords):
    """Yield (lineno, funcname, messages, comments) for gettext calls in model."""
    if (isinstance(model, Expression) and model and isinstance(model[0], Symbol)
            and str(model[0]) in keywords):
        args = model[1:]
        strings = [arg for arg in args if isinstance(arg, String)]
        if strings:
            messages = tuple(str(arg) if isinstance(arg, String) else None for arg in args)
            lineno = getattr(model, "start_line", None) or strings[0].start_line
            # lazy_gettext is flask-babel's lazy form of gettext
            funcname = "gettext" if str(model[0]) == "lazy_gettext" else str(model[0])
            yield lineno, funcname, messages[0] if len(messages) == 1 else messages, []
    if isinstance(model, tuple):
        for child in model:
            yield from _messages(child, keywords)


def extract_from_source(text, keywords=KEYWORDS, filename="<string>"):
    """Return the list of babel message tuples found in Hy source text."""
    keywords = set(keywords)
    return [message
            for form in hy.read_many(text, filename=filename, reader=_reader())
            for message in _messages(form, keywords)]


def babel_extract(fileobj, keywords=None, comment_tags=None, options=None):
    """Babel extraction method for Hy and HyML files."""
    options = options or {}
    text = fileobj.read()
    if isinstance(text, bytes):
        text = text.decode(options.get("encoding", "utf-8"))
    return iter(extract_from_source(text, set(KEYWORDS) | set(keywords or ()),
                                    getattr(fileobj, "name", "<string>")))
