#!/usr/bin/python3

# -*- coding: utf-8 -*-

import hy, hy.importer as hyi
from jinja2.ext import extract_from_ast
import itertools

def extract_from_ast(source, keywords):
    d = None
    def filter_hy(e):
        global d
        if isinstance(e, hy.HyExpression) or isinstance(e, list):
            if isinstance(e, hy.HyExpression):
                d = e[0]
            x = list(itertools.chain(*filter(None, map(filter_hy, e))))
            d = None
            return x
        elif not isinstance(e, hy.HySymbol) and isinstance(e, hy.HyString) and d in keywords:
            return 0, str(d), str(e)
    return filter_hy(source)

def chunks(l, n):
    if l:
        for i in range(0, len(l), n):
            t = l[i:i + n]
            yield tuple(t[:2]+[[t[2]]]+[[]])

def babel_extract(fileobj, *args, **kw):
    byte = fileobj.read()
    source = "".join(map(chr, byte))
    node = hyi.import_buffer_to_hst(source)
    # map keywords to hy symbols for later comparison
    if len(args[0]) > 0:
        keywords = map(hy.HySymbol, args[0])
    else:
        keywords = map(hy.HySymbol, ['ngettext', 'pgettext', 'ungettext', 'dngettext', 'dgettext', 'ugettext', 'gettext', '_', 'N_', 'npgettext'])
    ast = extract_from_ast(node, keywords)
    return chunks(ast, 3)
