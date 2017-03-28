#!/usr/bin/python3
# -*- coding: utf-8 -*-

import hy
from . minimal import *
from hy.importer import hy_eval, import_buffer_to_hst

def heval(tokens):
    try:
        return hy_eval(import_buffer_to_hst(tokens), {}, '<string>')
    except Exception as e:
    	print(e)

def peval(tokens):
	return heval("(print %s)" % tokens)

def ml(tokens):
	return heval("""
(require [hyml.minimal [*]])
(import (hyml.minimal (*)))
(print (ml %s))
""" % tokens)
