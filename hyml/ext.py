#!/usr/bin/python3

# -*- coding: utf-8 -*-

import hy, hy.importer as hyi
from jinja2.ext import extract_from_ast
import itertools

def extract_from_ast(source):
    d = None
    def filter_hy(e):
        global d
        if isinstance(e, hy.HyExpression) or isinstance(e, list):
            if isinstance(e, hy.HyExpression):
                d = e[0]
            x = list(itertools.chain(*filter(None, map(filter_hy, e))))
            d = None
            return x
        elif not isinstance(e, hy.HySymbol) and isinstance(e, hy.HyString):
            # ['ngettext', 'pgettext', 'ungettext', 'dngettext', 'dgettext', 'ugettext', 'gettext', '_', 'N_', 'npgettext']
            if d == hy.HySymbol("_") or d == hy.HySymbol("gettext"):
                return 0, str(d), str(e)
    return filter_hy(source)

def chunks(long_list, n):
    if long_list:
        for i in range(0, len(long_list), n):
            t = long_list[i:i + n]
            yield tuple(t[:2]+[[t[2]]]+[[]])

def babel_extract(fileobj, *args, **kw):
    byte = fileobj.read()
    text = "".join(map(chr, byte))
    node = hyi.import_buffer_to_hst(text)
    tpls = extract_from_ast(node)
    return chunks(tpls, 3)
