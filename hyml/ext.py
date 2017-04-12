#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) Marko Manninen <elonmedia@gmail.com>, 2017

import hy, hy.importer as hyi
from jinja2.ext import extract_from_ast
import itertools

def extract_from_ast(source, keywords):
    d = None
    def filter_hy(e):
        # basicly we are searching for babel keyword expressions here
        # and when one is found, it is returned along with:
        # 0 linenumber, keyword itself, and message string
        global d
        if isinstance(e, hy.HyExpression) or isinstance(e, list):
            if isinstance(e, hy.HyExpression):
                # this could be the keyword we are searching for
                d = e[0]
            # flatten list, maybe could be done later...
            x = list(itertools.chain(*filter(None, map(filter_hy, e))))
            # reset keyword
            d = None
            return x
        elif not isinstance(e, hy.HySymbol) and isinstance(e, hy.HyString) and d in keywords:
            # no comments available, thus only three items are returned
            # TODO: message context and plural message support
            return 0, str(d), {"context": str(e), "singular": str(e), "plural": str(e)}
    return filter_hy(source)

def chunks(long_list, n):
    # split list to n chunks
    for i in range(0, len(long_list), n):
        t = long_list[i:i + n]
        # add empty keyword list to the tuple for babel
        yield tuple(t[:2]+[t[2]["singular"]]+[[]])

def babel_extract(fileobj, *args, **kw):
    byte = fileobj.read()
    # unfortunately line breaks (line numbers) are lost at this point...
    source = "".join(map(chr, byte))
    if source:
        node = hyi.import_buffer_to_hst(source)
        if node:
            # map keywords to hy symbols for later comparison
            if len(args[0]) > 0:
                keywords = map(hy.HySymbol, args[0])
            else:
                keywords = map(hy.HySymbol, ['ngettext', 'pgettext', 'ungettext', 'dngettext', 'dgettext', 'ugettext', 'gettext', '_', 'N_', 'npgettext'])
            ast = extract_from_ast(node, keywords)
            if ast:
                return chunks(ast, 3)
