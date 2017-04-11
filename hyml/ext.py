#!/usr/bin/python3
# -*- coding: utf-8 -*-
import hy, hy.importer as hyi
from jinja2.ext import extract_from_ast
import itertools

def extract_from_ast(source, file=""):
    d = None
    def filter_hy(e):
        global d
        if isinstance(e, hy.HyExpression):
            d = e[0]
            return list(itertools.chain(*filter(None, map(filter_hy, e))))
        elif not isinstance(e, hy.HySymbol) and isinstance(e, hy.HyString):
            if d == hy.HySymbol("_") or \
               d == hy.HySymbol("gettext"):
                return file, d, e, []
    return filter_hy(source)

def chunks(l, n):
    if l:
        for i in range(0, len(l), n):
            yield tuple(l[i:i + n])

def babel_extract(fileobj, *args, **kw):
    byte = fileobj.read()
    print(byte)
    source = "".join(map(chr, byte))
    print(source)
    node = hyi.import_buffer_to_hst(source)[0]
    print(node)
    return chunks(extract_from_ast(node, fileobj.name), 4)
