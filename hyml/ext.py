#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from jinja2.ext import babel_extract as extract_jinja2

jinja_extensions = '''
                    hyml.ext.babel_extract, jinja2.ext.do, jinja2.ext.with_
                   '''

os.environ["VARIABLE_START_STRING"] = "(_ \""
os.environ["VARIABLE_END_STRING"] = "\")"

def babel_extract(fileobj, *args, **kw):
    kw['options']['extensions'] = jinja_extensions
    fileobj.read()
    raw_extract = extract_jinja2(fileobj, *args, **kw)
    fileobj.seek(0)
    for lineno, func, message, finder in raw_extract:
        yield lineno, func, message, finder
