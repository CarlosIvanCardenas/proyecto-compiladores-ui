from dataclasses import dataclass
from enum import Enum

class Operator(Enum):
    """
    Operadores disponibles para la clase Cuadruple.
    """
    PLUS = '+'
    MINUS = '-'
    TIMES = '*'
    DIVIDE = '/'
    ASSIGN = '='
    AND = '&&'
    OR = '||'
    LESSTHAN = '<'
    GREATERTHAN = '>'
    LESSTHANOREQ = '<='
    GREATERTHANOREQ = '>='
    EQUAL = '=='
    NOTEQUAL = '!='
    READ = 'read'
    WRITE = 'write'
    GOTO = 'goto'
    GOTOF = 'gotof'
    GOTOT = 'gotot'
    GOSUB = 'gosub'
    PARAMETER = 'parameter'
    ENDFUN = 'endfun'
    ERA = 'era'
    VERIFY = 'verify'
    # TODO: Agregar los que faltan

@dataclass
class Quadruple:
    operator: Operator
    left_operand: any
    right_operand: any
    result: any
