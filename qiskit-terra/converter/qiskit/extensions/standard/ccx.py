

from converter.qiskit import Gate
from converter.qiskit import QuantumCircuit
from converter.qiskit._instructionset import InstructionSet
from converter.qiskit._quantumregister import QuantumRegister
from converter.qiskit.extensions.standard import header  # pylint: disable=unused-import


class ToffoliGate(Gate):
    pass

    def __init__(self, ctl1, ctl2, tgt, circ=None):
        pass

    def inverse(self):
        pass

    def reapply(self, circ):
        pass


def ccx(self, ctl1, ctl2, tgt):
    pass



