#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) Marko Manninen <elonmedia@gmail.com>, 2017
#
# entry_points = """
#    [babel.extractors]
#    hyml = hyml.ext:babel_extract
#  """
#
# should be added to distutils setup.py file and then:
# 
# [hyml: **.hyml]
# [hyml: **.hy]
# extensions=hyml.ext.babel_extract
#
# to babel.cfg file


import hy, hy.importer as hyi
import itertools

def extract_from_ast(ast):
    d = None
    def filter_hy(e):
        # basicly we are searching for babel keyword expressions here
        # and when one is found, it is returned along with:
        # linenumber (0), keyword itself, and message string
        global d
        if isinstance(e, hy.HyExpression) or isinstance(e, list):
            if isinstance(e, hy.HyExpression):
                d = e[0]
            # recursively filter expression so that only gettext and _ parts are returned
            x = list(itertools.chain(*filter(None, map(filter_hy, e))))
            # reset keyword
            d = None
            return x
        elif not isinstance(e, hy.HySymbol) and isinstance(e, hy.HyString):
            # possible keys are:
            # ngettext, pgettext, ungettext, dngettext, dgettext, ugettext, gettext, _, N_, npgettext
            # but only  gettext and _ are supported at the moment
            if d == hy.HySymbol("_") or d == hy.HySymbol("gettext"):
                # there are no comments available in ast, thus only three items are returned
                # TODO: message context and plural message support could be done here
                return 0, str(d), str(e)
    return filter_hy(ast)

def chunks(long_list, n):
    # split list to n chunks
    if long_list:
        for i in range(0, len(long_list), n):
            t = long_list[i:i + n]
            # add empty keyword list to the tuple for babel
            yield tuple(t[:2]+[[t[2]]]+[[]])

def babel_extract(fileobj, *args, **kw):
    byte = fileobj.read()
    # unfortunately line breaks (line numbers) are lost at this point...
    text = "".join(map(chr, byte))
    node = hyi.import_buffer_to_hst(text)
    tpls = extract_from_ast(node)
    return chunks(tpls, 3)
