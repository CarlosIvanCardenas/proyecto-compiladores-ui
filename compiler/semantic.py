from compiler.semantic_cube import SemanticCube
from compiler.symbol_table import FunctionsDirectoryItem, VarTableItem, VarType, ConstType, ReturnType
from compiler.quadruple import Operator, Quadruple
from compiler.memory import VirtualMemoryManager


class SemanticActions:
    """
    Clase para manejar las acciones de los puntos neuralgicos del parser.

    Atributos:
        v_memory_manager:       Instancia de la clase VirtualMemoryManager.
        semantic_cube:          Instancia de la clase CuboSemantico.
        functions_directory:    Tabla que almacena la informacion de las funciones.
        global_var_table:       Tabla de variables globales.
        current_var_table:      Tabla de variables activa. Cambia cuando cambia el scope (tabla global o nueva funcion).
        const_table:            Tabla que asocia las constantes con una dirección de memoria.
        current_scope:          Scope activo.
        quad_list:              Lista de cuadruplos.
        operands_stack:         Pila de operandos (incluye tipo de dato).
        operators_stack:        Pila de operadores.
        jumps_stack:            Pila de saltos logicos en la lista de operandos.
        temp_vars_index:        Contador de variables temporales.
    """

    def __init__(self):
        self.v_memory_manager = VirtualMemoryManager()
        self.semantic_cube = SemanticCube()
        self.functions_directory = dict()
        self.global_var_table = dict()
        self.current_var_table = dict()
        self.const_table = dict()
        self.current_scope = 'global'
        self.quad_list = []
        self.operands_stack = []
        self.operators_stack = []
        self.jumps_stack = []
        self.temp_vars_index = 0

    def get_var(self, var_name):
        """
        Recuperar variable del diccionario de variables globales o del scope actual.
        Lanza una excepción si no se encuentra.

        :param var_name: Variable a buscar.
        :return: Una instancia de la clase VarTableItem.
        """
        var = self.current_var_table.get(var_name)
        if var is None:
            var = self.global_var_table.get(var_name)
            if var is None:
                var = self.current_var_table.get('_const_' + var_name)
                if var is None:
                    var = self.global_var_table.get('_const_' + var_name)
                    if var is None:
                        raise Exception("Undeclared variable: " + var_name)
        return var

    def get_fun(self, fun_name):
        """
        Recuperar función del diccionario de funciones.
        Lanza una excepción si no se encuentra.

        :param fun_name: Función a buscar.
        :return: Una instancia de la clase FunctionsDirectoryItem.
        """
        fun = self.functions_directory.get(fun_name)
        if fun is None:
            raise Exception('Undeclared function: ' + fun_name)
        return fun

    def set_global_scope(self):
        """
        Configuracion de la tabla actual de variables a variables globales y el scope actual a global
        """
        self.current_var_table = self.global_var_table
        self.current_scope = 'global'
        self.v_memory_manager.clear_mem()

    def set_current_scope(self, fun_name, return_type):
        """
        Configuracion de la tabla actual de variables a variables locales y el scope actual al nombre del
        modulo actual

        :param fun_name: Nombre del scope/función actual a declarar
        :param return_type: Tipo de retorno de la función
        """
        # Si la función no es VOID añadela a la memoria global.
        if return_type != ReturnType.VOID:
            function_id = "_fun_" + fun_name
            self.add_var(function_id, VarType(return_type.value), [])

        self.current_scope = fun_name
        self.functions_directory[fun_name] = FunctionsDirectoryItem(
            name=fun_name,
            return_type=return_type,
            param_table=[]
        )
        self.current_var_table = dict()

    def set_fun_start_addr(self):
        """
        Metodo para añadir el indice del cuadruplo equivalente a la primera instrucción de una función.
        """
        fun = self.get_fun(self.current_scope)
        fun.start_addr = len(self.quad_list)

    def end_fun(self):
        """
        Guarda los tamaños de las particiones de la memoria local (necesarios para ejecutar la instucción ERA en VM).
        Genera el cuadruplo con la instrucción ENDFUN.
        """
        # Save partition sizes for ERA instruction.
        fun = self.get_fun(self.current_scope)
        fun.local_partition_sizes = self.v_memory_manager.local_addr.get_partition_sizes()
        fun.temp_partition_sizes = self.v_memory_manager.temp_addr.get_partition_sizes()
        self.quad_list.append(Quadruple(Operator.ENDFUN, None, None, None))
        self.set_global_scope()

    def add_var(self, var_name, var_type, dims):
        """
        Añade variable a la tabla actual de variables

        :param var_name: Nombre de la variable a declarar
        :param var_type: Tipo de dato de la variable
        :param dims: Dimensiones de la variable (Si es de una dimensión, arreglo o matríz)
        """
        if len(dims) == 0:
            size = 1
            dimensions = (1, 0)
        elif len(dims) == 1:
            size = dims[0]
            dimensions = (dims[0], 0)
            self.get_const(dims[0], VarType.INT)
        else:
            size = dims[0] * dims[1]
            dimensions = (dims[0], dims[1])
            self.get_const(dims[0], VarType.INT)
            self.get_const(dims[1], VarType.INT)

        addr: int
        if self.current_scope == 'global':
            addr = self.v_memory_manager.global_addr.allocate_addr(var_type, size)
        else:
            addr = self.v_memory_manager.local_addr.allocate_addr(var_type, size)

        self.current_var_table[var_name] = VarTableItem(
            name=var_name,
            type=var_type,
            dims=dimensions,
            size=size,
            address=addr)

    def add_temp(self, var_name, var_type):
        """
        Añade variable temporal a la tabla actual de variables

        :param var_name: Nombre de la variable temporal a declarar
        :param var_type: Tipo de dato de la variable temporal
        :return: Dirección asignada a la nueva variable temporal
        """
        addr = self.v_memory_manager.temp_addr.allocate_addr(var_type)

        self.current_var_table[var_name] = VarTableItem(
            name=var_name,
            type=VarType(var_type),
            dims=(0, 0),
            size=1,
            address=addr)

        return addr

    def add_pointer(self, var_name, var_type):
        """
        Añade pointer a la tabla actual de variables

        :param var_name: Nombre de la variable temporal a declarar
        :param var_type: Tipo de dato de la variable temporal
        :return: Dirección asignada a la nueva variable temporal
        """
        addr = self.v_memory_manager.pointer_addr.allocate_addr(var_type)

        self.current_var_table[var_name] = VarTableItem(
            name=var_name,
            type=VarType(var_type),
            dims=(0, 0),
            size=1,
            address=addr)

        return addr

    def get_const(self, const_value, const_type):
        """
        Busca constante en tabla de constantes y si no existe la registra

        :param const_value: Valor de la constante a registrar
        :param const_type: Tipo de dato de la constante
        :return: Dirección asignada a la constante
        """
        const = self.const_table.get(str(const_value))
        if const is None:
            return self.add_const(const_value, const_type)
        else:
            if self.current_var_table.get(str(const_value)) is None:
                const_name = '_const_' + str(const_value)
                self.current_var_table[const_name] = const
            return const.address

    def add_const(self, const_value, const_type):
        """
        Añade constante a la tabla de constantes

        :param const_value: Valor de la constante a registrar
        :param const_type: Tipo de dato de la constante
        :return: Dirección asignada a la constante
        """
        var: VarTableItem
        if const_type == VarType.INT or const_type == VarType.FLOAT:
            addr = self.v_memory_manager.const_addr.allocate_addr(const_type)
            var = VarTableItem(
                name=str(const_value),
                type=VarType(const_type),
                dims=(1, 0),
                size=1,
                address=addr)
        else:
            addr = self.v_memory_manager.const_addr.allocate_addr(VarType.CHAR, len(const_value)-2)
            var = VarTableItem(
                name=str(const_value),
                type=VarType(const_type),
                dims=(len(const_value)-2, 0),
                size=len(const_value)-2,
                address=addr)

        self.const_table[str(const_value)] = var
        const_name = '_const_' + str(const_value)
        self.current_var_table[const_name] = var
        self.get_var(const_name)
        return addr

    def add_params(self, params):
        """
        Añade parametros de funcion a la tabla actual de variables y registra los parametros en la tabla de 
        funciones (los parametros no pueden ser arreglos ni matrices).

        :param params: Lista de parametros a declarar. Tupla (param_name, param_type)
        """
        params.reverse()
        for (param_name, param_type) in params:
            addr = self.v_memory_manager.local_addr.allocate_addr(param_type)
            self.functions_directory[self.current_scope].param_table.append((addr, param_type))
            self.current_var_table[param_name] = VarTableItem(
                name=param_name,
                type=param_type,
                dims=(0, 0),
                size=1,
                address=addr)

    def generate_quad(self):
        """
        Función para generar un cuadruplo utilizando las pilas de operadores, operandos y tipos
        """
        if len(self.operands_stack) >= 2 and len(self.operators_stack) >= 1 and self.operators_stack[-1] != '(':
            right_operand = self.get_var(self.operands_stack.pop())
            left_operand = self.get_var(self.operands_stack.pop())
            operator = Operator(self.operators_stack.pop())
            result_type = self.semantic_cube.type_match(left_operand.type, right_operand.type, operator)
            if result_type != "error":
                result_id = "_temp_" + str(self.temp_vars_index)
                result_addr = self.add_temp(result_id, result_type)
                self.temp_vars_index += 1
                self.quad_list.append(
                    Quadruple(Operator(operator), left_operand.address, right_operand.address, result_addr))
                self.operands_stack.append(result_id)
            else:
                raise Exception("Type mismatch")
        else:
            raise Exception("Operation stack error")

    def generate_quad_assign(self, name_var="", array=False):
        """
        Función para generar un cuadruplo de asignación utilizando la pila de operandos

        :param name_var: nombre de la variable donde se va a asignar el valor
        """
        if self.operands_stack:
            right_operand = self.get_var(self.operands_stack.pop())
            if array:
                left_operand = self.get_var(self.operands_stack.pop())
            else:
                left_operand = self.get_var(name_var)
            result_type = self.semantic_cube.type_match(left_operand.type, right_operand.type, Operator.ASSIGN)
            if result_type != "error":
                self.quad_list.append(Quadruple(Operator.ASSIGN, right_operand.address, None, left_operand.address))
            else:
                raise Exception("Type mismatch")
        else:
            raise Exception("Operation stack error")

    def push_var_operand(self, operand):
        """
        Añade una variable y su tipo a las pilas para generar cuadruplos

        :param operand: Operando a añadir
        """
        var = self.get_var(operand)
        self.operands_stack.append(var.name)

    def push_const_operand(self, const_value, const_type):
        """
        Añade una constante y su tipo a las pilas para generar cuadruplos

        :param operand: Operando a añadir
        """
        self.get_const(const_value, const_type)
        self.operands_stack.append(str(const_value))
        self.get_var(str(const_value))

    def generar_lectura(self, var_name):
        """
        Genera cuadruplo con operando de read y direccion de la variable que recibe el valor

        :var_name: Variable donde se guardara el valor a leer
        """
        var = self.get_var(var_name)
        self.quad_list.append(Quadruple(Operator.READ, None, None, var.address))

    def generar_escritura(self):
        """
        Genera cuadruplo con operando de write y el valor a escribir
        """
        addr: int
        if self.operands_stack:
            var_name = self.operands_stack.pop()
            var = self.get_var(var_name)
            self.quad_list.append(Quadruple(Operator.WRITE, None, None, var.address))
        else:
            raise Exception("Operation stack error")

    def start_if(self):
        """
        Genera cuadruplos necesarios al principio de un if
        """
        if self.operands_stack:
            res = self.get_var(self.operands_stack.pop())
            if res.type == VarType.BOOL:
                self.quad_list.append(Quadruple(Operator.GOTOF, res.address, None, None))
                self.jumps_stack.append(len(self.quad_list) - 1)
            else:
                raise Exception("Type mismatch")
        else:
            raise Exception("Operand stack error")

    def start_else(self):
        """
        Genera cuadruplos necesarios al principio de un else
        """
        self.quad_list.append(Quadruple(Operator.GOTO, None, None, None))
        if self.jumps_stack:
            false = self.jumps_stack.pop()
            self.jumps_stack.append(len(self.quad_list) - 1)
            self.finish_jump(false, len(self.quad_list))
        else:
            raise Exception("Jump stack error")

    def end_if(self):
        """
        Genera cuadruplos necesarios al final de un if
        """
        if self.jumps_stack:
            end = self.jumps_stack.pop()
            self.finish_jump(end, len(self.quad_list))
        else:
            raise Exception("Jump stack error")

    def start_while(self):
        """
        Establece saltos necesarios al principio de ciclo while
        """
        self.jumps_stack.append(len(self.quad_list))

    def expresion_while(self):
        """
        Genera cuadruplos necesarios al final de la expresion del while
        """
        if self.operands_stack:
            res = self.get_var(self.operands_stack.pop())
            if res.type == VarType.BOOL:
                self.quad_list.append(Quadruple(Operator.GOTOF, res.address, None, None))
                self.jumps_stack.append(len(self.quad_list) - 1)
            else:
                raise Exception("Type mismatch")
        else:
            raise Exception("Operand stack error")

    def end_while(self):
        """
        Completa saltos necesarios al final del ciclo while
        """
        if len(self.jumps_stack) >= 2:
            end = self.jumps_stack.pop()
            ret = self.jumps_stack.pop()
            self.quad_list.append(Quadruple(Operator.GOTO, None, None, ret))
            self.finish_jump(end, len(self.quad_list))
        else:
            raise Exception("Jump stack error")

    def start_for(self, id):
        """
        Verificaciones iniciales del ciclo for. Verifica que exista la vaaible de control y la agrega a los stacks

        :param id: nombre de la variable de control
        """
        var = self.get_var(id)
        if var.type == VarType.INT or var.type == VarType.FLOAT:
            self.operands_stack.append(var.name)
        else:
            raise Exception("Type mismatch")

    def valor_inicial_for(self):
        """
        Inicializa variable de control del ciclo for con valor de expresion
        """
        if len(self.operands_stack) >= 2:
            exp = self.get_var(self.operands_stack.pop())
            if exp.type == VarType.INT or exp.type == VarType.FLOAT:
                control = self.get_var(self.operands_stack.pop())
                tipo_res = self.semantic_cube.type_match(control.type, exp.type, Operator.ASSIGN)
                if tipo_res == VarType.INT or tipo_res == VarType.FLOAT:
                    self.quad_list.append(Quadruple(Operator.ASSIGN, exp.address, None, control.address))
                    self.operands_stack.append(control.name)
                else:
                    raise Exception("Type mismatch")
            else:
                raise Exception("Type mismatch")
        else:
            raise Exception("Operand stack error")

    def valor_final_for(self):
        """
        Establece valor final del ciclo for con valor de expresion
        """
        if len(self.operands_stack) >= 2:
            exp = self.get_var(self.operands_stack.pop())
            if exp.type == VarType.INT or exp.type == VarType.FLOAT:
                control = self.get_var(self.operands_stack.pop())
                if control.type == VarType.INT or control.type == VarType.FLOAT:
                    final = "_final_" + control.name
                    final_address = self.add_temp(final, exp.type)
                    self.quad_list.append(Quadruple(Operator.ASSIGN, exp.address, None, final_address))
                    temp = "_temp_" + str(self.temp_vars_index)
                    self.temp_vars_index += 1
                    temp_address = self.add_temp(temp, "bool")
                    self.quad_list.append(Quadruple(Operator('<'), control.address, final_address, temp_address))
                    self.jumps_stack.append(len(self.quad_list) - 1)
                    self.quad_list.append(Quadruple(Operator('gotof'), temp_address, None, None))
                    self.jumps_stack.append(len(self.quad_list) - 1)
                    self.operands_stack.append(control.name)
                else:
                    raise Exception("Type mismatch")
            else:
                raise Exception("Type mismatch")
        else:
            raise Exception("Operand stack error")

    def end_for(self):
        """
        Completa saltos necesarios al final del ciclo for
        """
        if len(self.jumps_stack) >= 2 and self.operands_stack:
            control = self.get_var(self.operands_stack.pop())
            temp = "_temp_" + str(self.temp_vars_index)  # Pedir dirección de memoria para el resultado
            self.temp_vars_index += 1
            tipo_res = self.semantic_cube.type_match(control.type, VarType.INT, Operator.PLUS)
            temp_address = self.add_temp(temp, tipo_res)
            self.quad_list.append(
                Quadruple(Operator('+'), control.address, self.get_const(1, VarType.INT), temp_address))
            self.quad_list.append(Quadruple(Operator.ASSIGN, temp_address, None, control.address))
            end = self.jumps_stack.pop()
            ret = self.jumps_stack.pop()
            self.quad_list.append(Quadruple(Operator('goto'), None, None, ret))
            self.finish_jump(end, len(self.quad_list))
        else:
            raise Exception("Stack error")

    def finish_jump(self, quad, jump):
        """
        Completa cuadruplo de salto con la informacion necesaria restante

        :param quad: Quad a completar
        :param jump: Informacion faltante de quad sobre a donde se hara el salto
        """
        if len(self.quad_list) > quad:
            self.quad_list[quad].result = jump
        else:
            raise Exception("Quadruple error, index out of bounds")

    def set_jump_main(self):
        """
        Genera quad de salto a main al inicio del programa
        """
        self.quad_list.append(Quadruple(Operator('goto'), None, None, None))
        self.jumps_stack.append(len(self.quad_list) - 1)

    def complete_main_jump(self):
        """
        Completa quad de salto a main
        """
        if self.jumps_stack:
            main = self.jumps_stack.pop()
            self.finish_jump(main, len(self.quad_list))
        else:
            raise Exception("Jump stack error")

    def fun_call(self, fun_name, arg_list, needs_return=False):
        """
        Genera las acciones necesarias para llamar a una función.
        Verifica coherencia en tipos y número de argumentos.

        :param fun_name: Nombre o identificador de la función a llamar.
        :param arg_list: Lista de argumentos de la llamada a función.
        """
        arg_list.reverse()
        # Verify that the function exists into the DirFunc
        fun = self.get_fun(fun_name)
        if needs_return and fun.return_type == ReturnType.VOID:
            raise Exception('Semantic Error: ' + fun.name + " is void. Return needed.")
        # Verify coherence in number of parameters
        if len(fun.param_table) != len(arg_list):
            raise Exception('Incorrect number of arguments in function call: ' + fun.name)
        # Generate action ERA size
        self.quad_list.append(Quadruple(Operator.ERA, None, None, fun.name))
        for index, (param, arg_name) in enumerate(zip(fun.param_table, arg_list)):
            arg = self.get_var(arg_name)
            # Verify coherence in types
            if param[1] == arg.type:
                self.quad_list.append(Quadruple(Operator.PARAMETER, arg.address, None, param[0]))
            else:
                raise Exception('Type mismatch, expected: ' + param[1] + " got: " + arg.type)
        # Generate action GOSUB
        self.quad_list.append(Quadruple(Operator.GOSUB, fun.name, None, fun.start_addr))

        # Save return value in a temp value
        if fun.return_type != ReturnType.VOID:
            fun_var = self.get_var("_fun_" + fun_name)
            temp_id = "_temp_" + str(self.temp_vars_index)
            temp_addr = self.add_temp(temp_id, fun_var.type)
            self.temp_vars_index += 1
            self.quad_list.append(Quadruple(Operator.ASSIGN, fun_var.address, None, temp_addr))
            self.operands_stack.append(temp_id)

    def return_stmt(self):
        """
        Metodo para añadir el indice del cuadruplo equivalente a la primera instrucción de una función.
        """
        if self.operands_stack:
            return_exp = self.operands_stack.pop()
            return_var = self.get_var(return_exp)
            fun_var = self.get_var("_fun_" + self.current_scope)
            result_type = self.semantic_cube.type_match(fun_var.type, return_var.type, Operator.ASSIGN)
            if result_type != "error":
                self.quad_list.append(Quadruple(Operator.ASSIGN, return_var.address, None, fun_var.address))
            else:
                raise Exception("Type mismatch")
        else:
            raise Exception("Operation stack error")

    def array_usage(self, var_id, dims):
        """
        Metodo adquirir direccion real de arreglo indexado y agregarlo al stack de operandos
        """
        var = self.get_var(var_id)
        if dims == 1:
            # Una dimension
            if var.dims[0] > 0:
                if self.operands_stack:
                    dim = self.operands_stack.pop()
                    dim_var = self.get_var(dim)
                    if dim_var.type == VarType.INT:
                        self.quad_list.append(
                            Quadruple(Operator.VERIFY, dim_var.address, self.get_const(0, VarType.INT),
                                      self.get_const(var.dims[0], VarType.INT)))
                        temp_id = "_temp_" + str(self.temp_vars_index)
                        temp_addr = self.add_temp(temp_id, var.type)
                        self.temp_vars_index += 1
                        self.quad_list.append(
                            Quadruple(Operator.PLUS, dim_var.address, self.get_const(var.address, VarType.INT),
                                      temp_addr))
                        # pointer_id tiene la direccion del arreglo indexado
                        pointer_id = "_pointer_" + str(self.temp_vars_index)
                        pointer_addr = self.add_pointer(pointer_id, var.type)
                        self.temp_vars_index += 1
                        self.quad_list.append(
                            Quadruple(Operator.ASSIGNPTR, temp_addr, '', pointer_addr))
                        self.operands_stack.append(pointer_id)
                    else:
                        raise Exception("Index type error")
                else:
                    raise Exception("Operation stack error")
            else:
                raise Exception("Var " + str(var_id) + " is not an array of 1 dimension")
        else:
            # Dos dimensiones
            if var.dims[0] > 0 and var.dims[1] > 0:
                if self.operands_stack:
                    dim2 = self.operands_stack.pop()
                    dim2_var = self.get_var(dim2)
                    dim1 = self.operands_stack.pop()
                    dim1_var = self.get_var(dim1)
                    if dim1_var.type == VarType.INT and dim2_var.type == VarType.INT:
                        self.quad_list.append(
                            Quadruple(Operator.VERIFY, dim1_var.address, self.get_const(0, VarType.INT),
                                      self.get_const(var.dims[0], VarType.INT)))
                        temp1_id = "_temp_" + str(self.temp_vars_index)
                        temp1_addr = self.add_temp(temp1_id, VarType.INT)
                        self.temp_vars_index += 1
                        self.quad_list.append(
                            Quadruple(Operator.TIMES, dim1_var.address, self.get_const(var.dims[1], VarType.INT),
                                      temp1_addr))
                        temp2_id = "_temp_" + str(self.temp_vars_index)
                        temp2_addr = self.add_temp(temp2_id, VarType.INT)
                        self.temp_vars_index += 1
                        self.quad_list.append(
                            Quadruple(Operator.PLUS, temp1_addr, self.get_const(var.address, VarType.INT), temp2_addr))
                        self.quad_list.append(
                            Quadruple(Operator.VERIFY, dim2_var.address, self.get_const(0, VarType.INT),
                                      self.get_const(var.dims[1], VarType.INT)))
                        temp3_id = "_temp_" + str(self.temp_vars_index)
                        temp3_addr = self.add_temp(temp3_id, VarType.INT)
                        self.temp_vars_index += 1
                        self.quad_list.append(
                            Quadruple(Operator.PLUS, temp2_addr, dim2_var.address, temp3_addr))
                        # pointer_id tiene la direccion del arreglo indexado
                        pointer_id = "_pointer_" + str(self.temp_vars_index)
                        pointer_addr = self.add_pointer(pointer_id, var.type)
                        self.temp_vars_index += 1
                        self.quad_list.append(Quadruple(Operator.ASSIGNPTR, temp3_addr, '', pointer_addr))
                        self.operands_stack.append(pointer_id)
                    else:
                        raise Exception("Index type error")
                else:
                    raise Exception("Operation stack error")
            else:
                raise Exception("Var " + str(var_id) + " is not an array of 2 dimensions")

# QuadList = SemanticActions.quad_list
# FuncDir = SemanticActions.functions_directory
# ConstTable = SemanticActions.const_table
