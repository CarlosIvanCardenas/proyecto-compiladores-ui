from dataclasses import dataclass
from compiler.quadruple import Quadruple
from compiler.symbol_table import VarTableItem, FunctionsDirectoryItem


@dataclass
class CompilerOutput:
    quadruples: [Quadruple]
    constants: [VarTableItem]
    functions_directory: [FunctionsDirectoryItem]
