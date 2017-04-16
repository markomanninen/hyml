#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
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

# special reader macro symbol for translating string less verbose way.
# instead of (_ "message") in hy you can do ㎕"message" as long as you have
# defined: (defreader ㎕ [args] `(_ ~@args)) in your program
readermacro = hy.HySymbol("㎕")

# accepted gettext / babel keywords
keywords = [hy.HySymbol("_"), 
            hy.HySymbol("gettext"), 
            hy.HySymbol("ngettext"), 
            hy.HySymbol("lgettext"), 
            hy.HySymbol("lngettext")]

# string and int are accepted as gettext messages
def is_message(e):
    return not isinstance(e, hy.HySymbol) and (isinstance(e, hy.HyString) or isinstance(e, hy.HyInteger))

# create message dictionary
def message(e, f):
    singular, plural, context = None, None, None
    if f == 0:
        singular = str(e)
    elif f == 1:
        plural = str(e)
    else:
        context = int(e)
    return {"context":context, "singular":singular, "plural":plural}

def extract_from_ast(ast):
    d, f = None, 0
    def filter_hy(e):
        # basicly we are searching for babel keyword expressions here
        # and when one is found, it is returned along with:
        # linenumber, keyword itself, and message string
        global d, f, keywords, readermacro
        print(e, e == readermacro, d == readermacro)
        if isinstance(e, hy.HyExpression) or isinstance(e, list):
            if isinstance(e, hy.HyExpression):
                d, f = e[0], 0
            # recursively filter expression so that only gettext and _ parts are returned
            x, f = list(itertools.chain(*filter(None, map(filter_hy, e)))), 0
            # reset keyword
            d = None
            return x
        if e == readermacro:
            d, f = e, 0
        elif is_message(e):
            # reader macro is regarded as singular form gettext function
            if d == readermacro:
                # we dont accept any more argument for gettext / readermacro
                d = None
                return e.start_line, "gettext", message(e, 0)
            # possible keys are:
            # ngettext, pgettext, ungettext, dngettext, dgettext, ugettext, gettext, _, N_, npgettext
            # but only  gettext and _ are supported at the moment
            if d in keywords:
                # there are no comments available in ast, thus only three items are returned
                # mark singular and plural forms. later in chunks
                # plural and singular forms are combined. this is not particularly genious 
                # way of doing it. other recursive parsing technique could handle everything
                # more efficiently
                msg = message(e, f)
                f += 1
                return e.start_line, str(d), msg
    return filter_hy(ast)

# return list of message items
def items(l, i, n):
    return l[i : i + n], l[i + n : i + n + n], l[i + n + n : i + n + n + n]

# detect plural and singular forms of messages
def message_form(t1, t2, t3):
    if t2 and "plural" in t2[2] and t2[2]["plural"] != None:
        return [t1[2]["singular"], t2[2]["plural"], t3[2]["context"]]
    else:
        return [t1[2]["singular"]]

# make extracted message list to 4 item chunks
def chunks(l, n):
    print(l, n)
    for i in range(0, len(l), n):
        t1, t2, t3 = items(l, i, n)
        if t1[2]["singular"] != None:
            # add empty keyword list to the tuple for babel
            yield tuple(t1[:2]+[message_form(t1, t2, t3)]+[[]])

def babel_extract(fileobj, *args, **kw):
    byte = fileobj.read()
    # unfortunately line breaks (line numbers) are lost at this point...
    text = "".join(map(chr, byte))
    node = hyi.import_buffer_to_hst(text)
    tpls = extract_from_ast(node)
    return chunks(tpls, 3)
