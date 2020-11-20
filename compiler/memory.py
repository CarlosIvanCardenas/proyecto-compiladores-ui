from compiler.symbol_table import VarType
from common.scope_size import GLOBAL_ADDRESS_RANGE, LOCAL_ADDRESS_RANGE, CONST_ADDRESS_RANGE, TEMP_ADDRESS_RANGE


class AddressBlock:
    """
    Clase que representa un bloque de direcciones virtuales de memoria, particionado en los 4 tipos de dato disponibles
    para el lenguaje.

    Atributos:
        int_addr:           Direccion inicial de memoria para la partición int.
        float_addr:         Direccion inicial de memoria para la partición float.
        char_addr:          Direccion inicial de memoria para la partición char.
        bool_addr:          Direccion inicial de memoria para la partición bool.
        int_addr_idx:       Indice de direcciones de memoria para la partición int.
        float_addr_idx:     Indice de direcciones de memoria para la partición float.
        char_addr_idx:      Indice de direcciones de memoria para la partición char.
        bool_addr_idx:      Indice de direcciones de memoria para la partición bool.
    """

    def __init__(self, start_addr, end_addr):
        self.start_addr = start_addr
        self.partition_size = (end_addr - start_addr + 1) // 4
        self.int_addr = start_addr
        self.float_addr = start_addr + self.partition_size
        self.char_addr = self.float_addr + self.partition_size
        self.bool_addr = self.char_addr + self.partition_size
        self.int_addr_idx = self.int_addr
        self.float_addr_idx = self.float_addr
        self.char_addr_idx = self.char_addr
        self.bool_addr_idx = self.bool_addr

    def allocate_addr(self, var_type, block_size=1):
        """
        Metodo para asignar un bloque de direcciones virtuales de memoria a una variable en una partición acorde a su
        tipo de dato.

        :param var_type: El tipo de dato de la variable a guardar en memoria.
        :param block_size: Tamaño del bloque de direcciones necesario. 1 por defecto.
        :return: Una dirección virual de memoria disponible para asignar la variable.
        """
        if var_type == VarType.INT:
            if self.int_addr_idx < self.float_addr:
                address = self.int_addr_idx
                self.int_addr_idx += block_size
            else:
                raise Exception('Int memory block overflow')
        elif var_type == VarType.FLOAT:
            if self.float_addr_idx < self.char_addr:
                address = self.float_addr_idx
                self.float_addr_idx += block_size
            else:
                raise Exception('Float memory block overflow')
        elif var_type == VarType.CHAR:
            if self.char_addr_idx < self.bool_addr:
                address = self.char_addr_idx
                self.char_addr_idx += block_size
            else:
                raise Exception('Char memory block overflow')
        else:  # VarType.BOOL
            if self.bool_addr_idx < self.bool_addr + self.partition_size:
                address = self.bool_addr_idx
                self.bool_addr_idx += block_size
            else:
                raise Exception('Bool memory block overflow')
        return address

    def get_partition_sizes(self):
        """
        Regresa los tamaños de las particiones de memoria por tipo de dato.

        :return: Un arreglo con los tamaños de las 4 particiones en orden: [int, float, char, bool]
        """
        int_size = self.int_addr_idx - self.start_addr
        float_size = self.float_addr_idx - self.float_addr
        char_size = self.char_addr_idx - self.char_addr
        bool_size = self.bool_addr_idx - self.bool_addr
        return [int_size, float_size, char_size, bool_size]

class VirtualMemoryManager:
    """
    Clase encargada de administrar las direcciones virtuales de memoria particionadas por scope.

    Atributos:
        global_addr:    Bloque de direcciones globales.
        local_addr:     Bloque de direcciones locales.
        const_addr:     Bloque de direcciones para constantes.
        temp_addr:      Bloque de direcciones temporales.
    """
    def __init__(self):
        self.global_addr = AddressBlock(GLOBAL_ADDRESS_RANGE[0], GLOBAL_ADDRESS_RANGE[1])
        self.local_addr = AddressBlock(LOCAL_ADDRESS_RANGE[0], LOCAL_ADDRESS_RANGE[1])
        self.const_addr = AddressBlock(CONST_ADDRESS_RANGE[0], CONST_ADDRESS_RANGE[1])
        self.temp_addr = AddressBlock(TEMP_ADDRESS_RANGE[0], TEMP_ADDRESS_RANGE[1])
        self.pointer_addr = AddressBlock(POINTER_ADDRESS_RANGE[0], POINTER_ADDRESS_RANGE[1])

    def clear_mem(self):
        """
        Restablece los bloques de direcciones locales y temporales.
        """
        self.local_addr = AddressBlock(LOCAL_ADDRESS_RANGE[0], LOCAL_ADDRESS_RANGE[1])
        self.temp_addr = AddressBlock(TEMP_ADDRESS_RANGE[0], TEMP_ADDRESS_RANGE[1])
