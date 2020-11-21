from dataclasses import dataclass
from common.scope_size import GLOBAL_ADDRESS_RANGE, LOCAL_ADDRESS_RANGE, CONST_ADDRESS_RANGE, TEMP_ADDRESS_RANGE, \
    POINTER_ADDRESS_RANGE
from compiler.quadruple import Operator, Quadruple
from compiler.symbol_table import VarType
from vm.memory import AddressBlock
from common.debug_flags import DEBUG_VM

"""
Esta clase se utiliza para guardar el contexto de ejecucion.
Contiene la posicion del instruction pointer, ademas del bloque
de memoria local correspondiente.
"""


@dataclass
class Frame:
    IP: int
    memory: AddressBlock


class VM:
    """
    Clase para simular la ejecución de una maquina virtual.

    Atributos:
        global_memory:      Partición de memoria para el scope global.
        temp_memory:        Partición de memoria para mantener valores auxiliares.
        execution_stack:    Lista de bloques de memoria para cada función del directorio de funciones.
        quad_list:          Lista de cuadruplos a ejecutar.
        const_memory:       Partición de memoria para los valores constantes (read-only).
        fun_dir:            Tabla que almacena la informacion de las funciones a ejecutar.
    """

    def __init__(self, quad_list, const_table, fun_dir):
        """
        Inicializa los atributos de la clase VM.

        :param quad_list: Lista de cuadruplos a ejecutar.
        :param const_table: Tabla que asocia las constantes con una dirección de memoria.
        :param fun_dir: Tabla que almacena la informacion de las funciones a ejecutar.
        """
        self.global_memory = AddressBlock(GLOBAL_ADDRESS_RANGE[0], GLOBAL_ADDRESS_RANGE[1])
        self.temp_memory = AddressBlock(TEMP_ADDRESS_RANGE[0], TEMP_ADDRESS_RANGE[1])
        self.pointer_memory = AddressBlock(POINTER_ADDRESS_RANGE[0], POINTER_ADDRESS_RANGE[1])
        self.execution_stack = [Frame(IP=0,
                                      memory=AddressBlock(LOCAL_ADDRESS_RANGE[0], LOCAL_ADDRESS_RANGE[1]))]
        self.next_exe_scope: ExeScope = None

        self.quad_list = quad_list
        self.const_memory = dict(map(lambda c: (c[1].address, c[1]), const_table.items()))
        self.fun_dir = fun_dir

    def get_current_frame(self):
        """
        Funcion que regresa el frame actual, el cual se encuentra al tope del stack de ejecucion
        :return: El frame actual de ejecucion
        """
        return self.execution_stack[-1]

    def get_current_memory(self):
        """
        Funcion que regresa la memoria local actual, la cual se encuentra dentro del frame al 
        tope del stack de ejecucion
        :return: La memoria local actual de ejecucion
        """
        current_frame = self.get_current_frame()
        return current_frame.memory

    def start_new_frame(self, IP, int_size, float_size, char_size, bool_size):
        """
        Genera un nuevo frame y lo guarda temporalmente en self.next_frame para preparar a la MV
        para el cambio de contexto.
        """
        # TODO: Definir bien los rangos del nuevo frame
        self.next_frame = Frame(IP=IP, memory=AddressBlock(
            LOCAL_ADDRESS_RANGE[0],
            LOCAL_ADDRESS_RANGE[1],
            int_size,
            float_size,
            char_size,
            bool_size))

    def switch_to_new_frame(self):
        """
        Anade el nuevo contexto al execution stack para completar el cambio de contexto una vez que la MV
        esta lista, y deja self.next_frame vacia.
        """
        self.execution_stack.append(self.next_frame)
        self.next_frame = None

    def restore_past_frame(self):
        """
        Elimina el frame actual cuando la funcion que lo necesitaba termina su ejecucion
        """
        self.execution_stack.pop()

    def write(self, addr, value):
        """
        Función auxiliar para escribir un valor en una dirección de memoria.
        Verifica a que partición de memoria por scope pertenece la dirección.

        :param addr: Dirección (absoluta) en la cual se desea escribir.
        :param value: Valor que se desea escribir en memoria.
        """
        if GLOBAL_ADDRESS_RANGE[0] <= addr < GLOBAL_ADDRESS_RANGE[1]:
            self.global_memory.write(addr, value)
        elif LOCAL_ADDRESS_RANGE[0] <= addr < LOCAL_ADDRESS_RANGE[1]:
            self.get_current_memory().write(addr, value)
        elif CONST_ADDRESS_RANGE[0] <= addr < CONST_ADDRESS_RANGE[1]:
            raise MemoryError('Cannot to write to read-only memory')
        elif TEMP_ADDRESS_RANGE[0] <= addr < TEMP_ADDRESS_RANGE[1]:
            self.temp_memory.write(addr, value)
        elif POINTER_ADDRESS_RANGE[0] <= addr < POINTER_ADDRESS_RANGE[1]:
            real_addr = self.pointer_memory.read(addr)
            self.write(real_addr, value)
        else:
            raise MemoryError('Address out of bounds')

    def read(self, addr):
        """
        Función auxiliar para leer el valor asignado a una dirección de memoria.
        Verifica a que partición de memoria por scope pertenece la dirección.

        :param addr: Dirección (absoluta) de la cual se desea leer un valor.
        :return: El valor asignado en la dirección "addr".
        """
        # FOR DEBUG PURPOSES
        if addr is None:
            return ''
        if type(addr) is str:
            return addr

        if GLOBAL_ADDRESS_RANGE[0] <= addr < GLOBAL_ADDRESS_RANGE[1]:
            return self.global_memory.read(addr)
        elif LOCAL_ADDRESS_RANGE[0] <= addr < LOCAL_ADDRESS_RANGE[1]:
            return self.get_current_memory().read(addr)
        elif CONST_ADDRESS_RANGE[0] <= addr < CONST_ADDRESS_RANGE[1]:
            const = self.const_memory[addr]
            if const.type == VarType.INT:
                return int(const.name)
            elif const.type == VarType.FLOAT:
                return float(const.name)
            else:
                return const.name
        elif TEMP_ADDRESS_RANGE[0] <= addr < TEMP_ADDRESS_RANGE[1]:
            return self.temp_memory.read(addr)
        elif POINTER_ADDRESS_RANGE[0] <= addr < POINTER_ADDRESS_RANGE[1]:
            real_addr = self.pointer_memory.read(addr)
            return self.read(real_addr)
        else:
            raise MemoryError('Address out of bounds')

    def read_block(self, addr, size):
        """
        Función auxiliar para leer los valores asignados a un bloque continuo de direcciones de memoria.
        Verifica a que partición de memoria por scope pertenece la dirección.

        :param addr: Dirección (absoluta) de la cual se desea leer un valor.
        :param size: Tamaño del bloque.
        :return: El valor asignado en la dirección "addr".
        """
        if GLOBAL_ADDRESS_RANGE[0] <= addr < GLOBAL_ADDRESS_RANGE[1]:
            return self.global_memory.read_block(addr, size)
        elif LOCAL_ADDRESS_RANGE[0] <= addr < LOCAL_ADDRESS_RANGE[1]:
            return self.get_current_memory().read_block(addr, size)
        elif CONST_ADDRESS_RANGE[0] <= addr < CONST_ADDRESS_RANGE[1]:
            raise MemoryError('There is not const arrays')
        elif TEMP_ADDRESS_RANGE[0] <= addr < TEMP_ADDRESS_RANGE[1]:
            return self.temp_memory.read_block(addr, size)
        elif POINTER_ADDRESS_RANGE[0] <= addr < POINTER_ADDRESS_RANGE[1]:
            real_addr = self.pointer_memory.read_block(direct, size)
            return self.read(real_addr)
        else:
            raise MemoryError('Address out of bounds')

    def next_instruction(self):
        """
        Se extrae el siguiente cuadruplo a ejecutar y se extrae su operador asi como los operandos involucrados.
        Para las operaciones aritmeticas se realiza la operacion establecida con los operandos A y B y se guarda
        el resultado en el operando C
        """
        frame = self.get_current_frame()
        current_quad: Quadruple
        current_quad = self.quad_list[frame.IP]
        instruction = current_quad.operator
        A = current_quad.left_operand
        B = current_quad.right_operand
        C = current_quad.result

        if DEBUG_VM:
            print(f'{frame.IP}.\t{instruction}\tA:{A}\tB:{B}\tC:{C}')

        if instruction == Operator.PLUS:
            self.write(C, self.read(A) + self.read(B))
        elif instruction == Operator.MINUS:
            self.write(C, self.read(A) - self.read(B))
        elif instruction == Operator.TIMES:
            self.write(C, self.read(A) * self.read(B))
        elif instruction == Operator.DIVIDE:
            self.write(C, self.read(A) / self.read(B))
        elif instruction == Operator.ASSIGN:
            self.write(C, self.read(A))
        elif instruction == Operator.AND:
            self.write(C, self.read(A) and self.read(B))
        elif instruction == Operator.OR:
            self.write(C, self.read(A) or self.read(B))
        elif instruction == Operator.LESSTHAN:
            self.write(C, self.read(A) < self.read(B))
        elif instruction == Operator.GREATERTHAN:
            self.write(C, self.read(A) > self.read(B))
        elif instruction == Operator.LESSTHANOREQ:
            self.write(C, self.read(A) <= self.read(B))
        elif instruction == Operator.GREATERTHANOREQ:
            self.write(C, self.read(A) >= self.read(B))
        elif instruction == Operator.EQUAL:
            self.write(C, self.read(A) == self.read(B))
        elif instruction == Operator.NOTEQUAL:
            self.write(C, self.read(A) != self.read(B))
        elif instruction == Operator.READ:
            """
            READ se encarga de leer el input del usuario, Este input se recoge y se intenta hacer un cast al tipo
            de la variable donde se guardara el input.
            """
            # TODO: Revisar como implementar en UI
            var_type = frame.memory.get_partition(B)
            user_input = input()
            if var_type == VarType.INT:
                try:
                    user_input = int(user_input)
                except:
                    raise TypeError("Can not cast input to int")
            elif var_type == VarType.FLOAT:
                try:
                    user_input = float(user_input)
                except:
                    raise TypeError("Can not cast input to float")
            elif var_type == VarType.CHAR:
                try:
                    user_input = str(user_input)
                except:
                    raise TypeError("Can not cast input to char")
            elif var_type == VarType.BOOL:
                try:
                    user_input = bool(user_input)
                except:
                    raise TypeError("Can not cast input to bool")
            self.write(C, user_input)
        elif instruction == Operator.WRITE:
            """
            WRITE escribe en pantalla el valor que se recoge de la variable que se intenta escribir.
            """
            # TODO: Revisar como implementar en UI
            value = self.read(C)
            if type(value) == str:
                value = value.replace('\\n', '\n')
            print(value)
        elif instruction == Operator.GOTO:
            """
            GOTO actualiza el valor del instruction pointer hacia la direccion del salto
            """
            frame.IP = C
            return
        elif instruction == Operator.GOTOF:
            """
            GOTOF actualiza el valor del instruction pointer hacia la direccion del salto siempre y cuando el valor
            del operando A sea falso
            """
            if not self.read(A):
                frame.IP = C
                return
        elif instruction == Operator.GOTOT:
            """
            GOTOT actualiza el valor del instruction pointer hacia la direccion del salto siempre y cuando el valor
            del operando A sea verdadero
            """
            if self.read(A):
                frame.IP = C
                return
        elif instruction == Operator.GOSUB:
            """
            Adelanta el IP a la siguiente instruccion a ejecutar despues de terminar con la funcion y termina 
            el cambio de contexto al llamar a switch_to_new_frame
            """
            frame.IP += 1
            self.switch_to_new_frame()
            return

        elif instruction == Operator.PARAMETER:
            """
            Esta funcion se utiliza para mapear los valores para el parametro C en el contexto
            de ejecucion proximo a despertar.
            """
            self.next_frame.memory.write(C, self.read(A))

        elif instruction == Operator.ENDFUN:
            """
            Elimina el frame (y con eso el contexto de ejecucion) de la funcion que haya terminado su ejecucion.
            """
            self.restore_past_frame()
            return
        elif instruction == Operator.ERA:
            """
            ERA inicializa un nuevo frame para preparar a la maquina virtual para el cambio de contexto que
            ocurre al llamarse una funcion. El nuevo frame sera incializado con la informacion correspondiente de
            la funcion a ejecutar (su direccion de inicio y los tamanos requeridos para sus variables).
            """
            self.start_new_frame(
                IP=self.fun_dir[C].start_addr,
                int_size=self.fun_dir[C].partition_sizes[0],
                float_size=self.fun_dir[C].partition_sizes[1],
                char_size=self.fun_dir[C].partition_sizes[2],
                bool_size=self.fun_dir[C].partition_sizes[3],
            )
        elif instruction == Operator.VERIFY:
            """
            VERIFY se asegura de que el indice A este entre los limites B y C, que corresponden a los limites de la
            dimension correspondiente de un arreglo
            """
            index = int(self.read(A))
            if not B <= index < C:
                raise Exception("Index out of bounds")

        frame.IP += 1

    def run(self):
        """
        Ejecuta todas las intrucciones de la quad_list
        """
        if DEBUG_VM:
            print("\nInicio ejecución:")
        while self.get_current_frame().IP < len(self.quad_list):
            self.next_instruction()
