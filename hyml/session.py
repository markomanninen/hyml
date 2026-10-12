# -*- coding: utf-8 -*-
"""Run Hy source text form by form in one module, the way a REPL does."""

import types

import hy
from hy.reader import HyReader


class HySession:
    """Evaluate Hy source in a persistent module namespace.

    Names, macros and reader macros defined by one ``run`` call are
    available in the later ones.
    """

    def __init__(self, module=None, namespace=None):
        self.module = module if module is not None else types.ModuleType("__hy_session__")
        self.namespace = namespace if namespace is not None else vars(self.module)
        # one reader for the whole session, so that reader macros stay enabled
        self.reader = HyReader()

    def run(self, source, filename="<hy-session>"):
        """Evaluate the source and return the value of its last form."""
        result = None
        # forms are read one at a time, so a reader macro required by one
        # form can be used by the next one
        for form in hy.read_many(source, filename=filename, reader=self.reader):
            result = hy.eval(form, self.namespace, module=self.module)
            self.reader.reader_macros.update(vars(self.module).get("_hy_reader_macros", {}))
        return result
