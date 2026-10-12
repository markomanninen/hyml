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

from IPython.core.magic import Magics, cell_magic, line_magic, magics_class

from hyml.session import HySession


@magics_class
class HyMagics(Magics):

    def __init__(self, shell):
        super().__init__(shell)
        self.session = HySession(shell.user_module, shell.user_ns)

    def run(self, source):
        return self.session.run(source, "<hy-cell>")

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
