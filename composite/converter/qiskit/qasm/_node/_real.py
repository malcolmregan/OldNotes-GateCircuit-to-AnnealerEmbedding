

from sympy import latex, pi
from sympy.printing.ccode import ccode
from ._node import Node


class Real(Node):
    pass


    def __init__(self, id):
        pass

    def to_string(self, indent):
        pass

    def qasm(self, prec=15):
        pass


    def latex(self, prec=15, nested_scope=None):
        pass

    def sym(self, nested_scope=None):
        pass

    def real(self, nested_scope=None):
        pass
