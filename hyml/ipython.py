# -*- coding: utf-8 -*-
"""IPython / Jupyter extension for running Hy code in notebook cells.

There is no maintained Hy kernel, so HyML notebooks use the standard
Python kernel with this extension::

    %load_ext hyml.ipython

    %%hy
    (require hyml.minimal *)
    (ml (p :class "x" "Hello"))

The value of the last form of a cell is the cell's output. Macros and
reader macros required in one cell are available in later cells.
"""

import hy
from hy.reader import HyReader
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class


@magics_class
class HyMagics(Magics):

    def __init__(self, shell):
        super().__init__(shell)
        # one reader for the whole session, so that reader macros stay enabled
        self.reader = HyReader()

    def run(self, source):
        module = self.shell.user_module
        result = None
        # forms are read one at a time, so a reader macro required by one
        # form can be used by the next one in the same cell
        for form in hy.read_many(source, filename="<hy-cell>", reader=self.reader):
            result = hy.eval(form, self.shell.user_ns, module=module)
            self.reader.reader_macros.update(vars(module).get("_hy_reader_macros", {}))
        return result

    @cell_magic
    def hy(self, line, cell):
        """Run the cell as Hy code."""
        return self.run(cell)

    @line_magic("hy")
    def hy_line(self, line):
        """Run the rest of the line as Hy code."""
        return self.run(line)


def load_ipython_extension(ipython):
    ipython.register_magics(HyMagics)
