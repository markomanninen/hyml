#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from jinja2.ext import babel_extract as extract_jinja2

os.environ["VARIABLE_START_STRING"] = "(_ \""
os.environ["VARIABLE_END_STRING"] = "\")"

def babel_extract(fileobj, *args, **kw):
    kw['options']['extensions'] = "hyml.ext.babel_extract"
    fileobj.read()
    raw_extract = extract_jinja2(fileobj, *args, **kw)
    fileobj.seek(0)
    for lineno, func, message, finder in raw_extract:
        yield lineno, func, message, finder
