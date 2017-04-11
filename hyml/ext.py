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
            d = e[0]
            return list(itertools.chain(*filter(None, map(filter_hy, e))))
        elif not isinstance(e, hy.HySymbol) and isinstance(e, hy.HyString):
            if d == hy.HySymbol("_") or \
               d == hy.HySymbol("gettext"):
                return 0, str(d), e
            else:
                d = None
    return filter_hy(source)

def chunks(l, n):
    if l:
        for i in range(0, len(l), n):
            t = l[i:i + n]
            yield tuple(t[:2]+[[t[2]]]+[[]])

def babel_extract(fileobj, *args, **kw):
    print([fileobj, args, kw])
    byte = fileobj.read()
    source = "".join(map(chr, byte))
    node = hyi.import_buffer_to_hst(source)
    print(node)
    chunk = chunks(extract_from_ast(node), 3)
    print(list(chunk))
    return chunk
