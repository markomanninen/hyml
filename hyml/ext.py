#!/usr/bin/python3
# -*- coding: utf-8 -*-
#---------------------------------------------------------
# Copyright (c) Marko Manninen <elonmedia@gmail.com>, 2017
#---------------------------------------------------------
#
# Usage:
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
#
#-----------------------------------------------------------------------
# LOCALIZATION ROUTINE
#-----------------------------------------------------------------------
# 1. extract messages:
# pybabel extract -F babel.cfg -o messages.pot .
# 2. initialize language file:
# pybabel init -i messages.pot -d translations -l en
# 3. make changes to the language file (manually or via third party app)
# 4. update translation messages:
# pybabel update -i messages.pot -d translations
# 5. compile translations
# pybabel compile -d translations
#-----------------------------------------------------------------------

import hy, hy.importer as hyi
import itertools

# special reader macro symbol for translating string less verbose way.
# instead of (_ "message") in hy you can do i"message" as long as you have
# defined: (defsharp i [args] `(_ ~args)) in your program
readermacro, dispatch_reader_macro = hy.HySymbol("i"), hy.HySymbol("dispatch_reader_macro")
# lazy_gettext is a special keyword for flask babel
gettext, lazy_gettext = hy.HySymbol("gettext"), hy.HySymbol("lazy_gettext")
# accepted gettext / babel keywords
keywords = [hy.HySymbol("_"), 
            gettext, 
            hy.HySymbol("ngettext"), 
            hy.HySymbol("N_"), 
            hy.HySymbol("lgettext"), 
            hy.HySymbol("lngettext"), 
            lazy_gettext]

# string and int are accepted as gettext messages
def is_message(expr):
    return not isinstance(expr, hy.HySymbol) and (isinstance(expr, hy.HyString) or isinstance(expr, hy.HyInteger))

# create message dictionary
def message(expr, count):
    singular, plural, num = None, None, None
    if count == 0:
        singular = str(expr)
    elif count == 1:
        plural = str(expr)
    else:
        num = int(expr)
    return {"num":num, "singular":singular, "plural":plural}

def extract_from_ast(ast):
    current, count, prev, dispatch = None, 0, None, False
    def filter_hy(expr):
        # basicly we are searching for babel keyword expressions here
        # and when one is found, it is returned along with:
        # linenumber, keyword itself, and message string
        global current, count, prev, dispatch
        if isinstance(expr, hy.HyExpression) or isinstance(expr, list):
            if isinstance(expr, hy.HyExpression):
                current, count, prev, dispatch = expr[0], 0, None, False
            # recursively filter expression so that only gettext and _ parts are returned
            messages = list(itertools.chain(*filter(None, map(filter_hy, expr))))
            # reset keyword
            current, count, prev, dispatch = None, 0, None, False
            return messages
        if expr == readermacro and prev == dispatch_reader_macro:
            current, count, dispatch = expr, 0, True
        elif is_message(expr):
            # reader macro is regarded as singular form gettext function
            if current == readermacro and dispatch:
                # we dont accept any more argument for gettext / readermacro
                current, prev, dispatch = None, None, False
                return expr.start_line, "gettext", message(expr, 0)
            # possible keys are:
            # ngettext, pgettext, ungettext, dngettext, dgettext, ugettext, gettext, _, N_, npgettext
            # but only  gettext and _ are supported at the moment
            if current in keywords:
                # there are no comments available in ast, thus only three items are returned
                # mark singular and plural forms. later in chunks
                # plural and singular forms are combined. this is not particularly genious 
                # way of doing it. other recursive parsing technique could handle everything
                # more efficiently
                msg = message(expr, count)
                count += 1
                if current == lazy_gettext:
                    key = str(gettext)
                else:
                    key = str(current)
                return expr.start_line, key, msg
        prev = expr
    return filter_hy(ast)

# return list of message items
def items(l, i, n):
    return l[i : i + n], l[i + n : i + n + n], l[i + n + n : i + n + n + n]

# detect plural and singular forms of messages
def message_form(t1, t2, t3):
    if t2 and "plural" in t2[2] and t2[2]["plural"] != None:
        return [t1[2]["singular"], t2[2]["plural"], t3[2]["num"]]
    else:
        return [t1[2]["singular"]]

# make extracted message list to 4 item chunks
def chunks(l, n):
    for i in range(0, len(l), n):
        t1, t2, t3 = items(l, i, n)
        if t1[2]["singular"] != None:
            # add empty keyword list to the tuple for babel
            yield tuple(t1[:2]+[message_form(t1, t2, t3)]+[[]])

def babel_extract(fileobj, *args, **kw):
    byte = fileobj.read()
    text = "".join(map(chr, byte))
    node = hyi.import_buffer_to_hst(text)
    tpls = extract_from_ast(node)
    return chunks(tpls, 3)
