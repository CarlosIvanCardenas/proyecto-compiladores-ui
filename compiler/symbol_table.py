from dataclasses import dataclass
from enum import Enum

class VarType(Enum):
    """
    Tipos de dato disponibles para una variable.
    """
    INT = 'int'
    FLOAT = 'float'
    CHAR = 'char'
    BOOL = 'bool'

class ReturnType(Enum):
    """
    Tipos de retorno disponibles para una función.
    """
    VOID = 'void'
    INT = 'int'
    FLOAT = 'float'
    CHAR = 'char'

class ConstType(Enum):
    """
    Tipos de dato disponibles para una constante (ej: 4, 1.2, "Test", 'a').
    """
    int = int
    float = float
    string = str
    char = str

@dataclass
class FunctionsDirectoryItem:
    """
    Se tendra un diccionario que actue como Directorio de Procedimientos que almacene tuplas del tipo
    (FunctionsDirectoryItem, list(VarTableItem)) por cada funcion del programa ademas del registro global
    """
    name: str
    return_type: ReturnType
    param_table: list = None
    start_addr: int = None
    partition_sizes: [int, int, int, int] = None

@dataclass
class VarTableItem:
    """
    Se tendra un objeto ElementoTablaVariables por cada variable declarada dentro de un procedimiento, misma que se
    almacenara en su correspondiente lista dentro del Directorio de Procedimientos.
    """
    name: str
    type: VarType
    size: int
    address: int
    value: ConstType = None
    dims: (int, int) = (None, None)
