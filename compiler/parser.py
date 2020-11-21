from sly.yacc import Parser as SlyParser
from compiler.lexer import Tokens
from compiler.semantic import SemanticActions
from compiler.symbol_table import ReturnType, VarType
from compiler.output import CompilerOutput
from common.debug_flags import DEBUG_PARSER

class CompParser(SlyParser):
    # Define starting grammar
    start = 'program'
    # Get the token list from the lexer
    tokens = Tokens

    semantics = SemanticActions()

    # Grammar rules and actions
    @_('jump_main ID set_global vars funs main')
    def program(self, p):
        if DEBUG_PARSER:
            print('Regla: program ' + p.ID)
        return CompilerOutput(quadruples=self.semantics.quad_list,
                              constants=self.semantics.const_table,
                              functions_directory=self.semantics.functions_directory)
    
    @_('PROGRAM')
    def jump_main(self, _):
        if DEBUG_PARSER:
            print('Regla: jump_main')
        self.semantics.set_jump_main()
    
    @_('')
    def set_global(self, _):
        self.semantics.set_global_scope()
        if DEBUG_PARSER:
            print('Regla: set_global')

    # Declaracion de VARIABLES GLOBALES
    @_('var vars', 'empty')
    def vars(self, _):
        if DEBUG_PARSER:
            print('Regla: vars')
        pass

    @_('VAR ID array_dec ":" tipo')
    def var(self, p):
        self.semantics.add_var(var_name=p.ID, var_type=VarType(p.tipo), dims=p.array_dec)
        if DEBUG_PARSER:
            print('Regla: var con ' + p.ID)
        pass

    # TIPO de variables
    @_('INT', 'FLOAT', 'CHAR')
    def tipo(self, p):
        if DEBUG_PARSER:
            print('Regla: tipo ' + p[0])
        return p[0]

    # Declaracion de FUNCIONES
    @_('fun funs', 'fun_void funs', 'empty')
    def funs(self, _):
        if DEBUG_PARSER:
            print('Regla: funs')
        pass

    # FUNCION
    @_('fun_header set_start_addr bloque_return')
    def fun(self, _):
        if DEBUG_PARSER:
            print('Regla: fun')
        self.semantics.end_fun()
        pass

    @_('FUN ID param_list return_type')
    def fun_header(self, p):
        if DEBUG_PARSER:
            print('Regla: fun_header ' + p.ID)
        self.semantics.set_current_scope(p.ID, ReturnType(p.return_type))
        self.semantics.add_params(p.param_list)
        pass

    @_('fun_header_void set_start_addr bloque')
    def fun_void(self, _):
        if DEBUG_PARSER:
            print('Regla: fun')
        self.semantics.end_fun()
        pass

    @_('FUN ID param_list ":" VOID')
    def fun_header_void(self, p):
        if DEBUG_PARSER:
            print('Regla: fun_header ' + p.ID)
        self.semantics.set_current_scope(p.ID, ReturnType("void"))
        self.semantics.add_params(p.param_list)
        pass

    @_('')
    def set_start_addr(self, _):
        self.semantics.set_fun_start_addr()
        pass

    @_('":" tipo')
    def return_type(self, p):
        if DEBUG_PARSER:
            print('Regla: return_type')
        return p[1]

    # RETURN
    @_('RETURN "(" expresion ")"')
    def return_stmt(self, _):
        self.semantics.return_stmt()
        if DEBUG_PARSER:
            print('Regla: return_stmt')
        pass

    # Declaracion de PARAMETROS
    @_('"(" params ")"')
    def param_list(self, p):
        if DEBUG_PARSER:
            print('Regla: param_list')
        return p.params

    @_('"(" empty ")"')
    def param_list(self, _):
        if DEBUG_PARSER:
            print('Regla: param_list is empty')
        return []

    @_('ID ":" tipo params_aux')
    def params(self, p):
        if DEBUG_PARSER:
            print('Regla: params')
        p.params_aux.append((p.ID, VarType(p.tipo)))
        return p.params_aux

    @_('"," params')
    def params_aux(self, p):
        if DEBUG_PARSER:
            print('Regla: params_aux')
        return p.params

    @_('empty')
    def params_aux(self, _):
        if DEBUG_PARSER:
            print('Regla: params_aux is empty')
        return []

    # MAIN
    @_('start_main bloque')
    def main(self, _):
        if DEBUG_PARSER:
            print('Regla: main')
        pass

    @_('MAIN "(" ")"')
    def start_main(self, _):
        self.semantics.complete_main_jump()
        self.semantics.set_current_scope("main", ReturnType("void"))
        if DEBUG_PARSER:
            print('Regla: start_main')
        pass

    # BLOQUE
    @_('"{" estatutos "}"')
    def bloque(self, _):
        if DEBUG_PARSER:
            print('Regla: bloque')
        pass

    @_('"{" estatutos return_stmt "}"', '"{" return_stmt "}"')
    def bloque_return(self, _):
        if DEBUG_PARSER:
            print('Regla: bloque_return')
        pass

    # ESTATUTOS
    @_('estatuto estatutos1')
    def estatutos(self, _):
        if DEBUG_PARSER:
            print('Regla: estatutos')
        pass

    @_('estatutos', 'empty')
    def estatutos1(self, _):
        if DEBUG_PARSER:
            print('Regla: estatutos1')
        pass

    @_('asignacion', 'condicion', 'lectura', 'escritura', 'ciclo_for', 'ciclo_while', 'call_fun', 'var')
    def estatuto(self, _):
        if DEBUG_PARSER:
            print('Regla: estatuto')
        pass

    # LLAMADA A FUNCIÓN
    @_('ID arg_list')
    def call_fun(self, p):
        if DEBUG_PARSER:
            print('Regla: call_fun ' + str(p.ID))
        self.semantics.fun_call(p[0], p.arg_list)
        pass

    @_('ID arg_list')
    def call_fun_no_void(self, p):
        if DEBUG_PARSER:
            print('Regla: call_fun no void ' + str(p.ID))
        self.semantics.fun_call(p[0], p.arg_list, needs_return=True)
        pass

    # ARGUMENTOS DE LLAMADA A FUNCIÓN
    @_('add_fondo_arg_list args remove_fondo_arg_list')
    def arg_list(self, p):
        if DEBUG_PARSER:
            print('Regla: arg_list')
        return p.args

    @_('"(" ")"')
    def arg_list(self, _):
        if DEBUG_PARSER:
            print('Regla: arg_list empty')
        return []

    @_('add_fondo_arg exp remove_fondo_arg args_aux')
    def args(self, p):
        if DEBUG_PARSER:
            print('Regla: arg exp')
        p.args_aux.append((self.semantics.operands_stack.pop()))
        return p.args_aux

    @_('"," args')
    def args_aux(self, p):
        if DEBUG_PARSER:
            print('Regla: arg_aux')
        return p.args

    @_('empty')
    def args_aux(self, _):
        if DEBUG_PARSER:
            print('Regla: arg_aux empty')
        return []

    @_('"("')
    def add_fondo_arg_list(self, _):
        self.semantics.operators_stack.append('(')
        if DEBUG_PARSER:
            print('Regla: add_fondo arg list')
        pass

    @_('")"')
    def remove_fondo_arg_list(self, _):
        self.semantics.operators_stack.pop()
        if DEBUG_PARSER:
            print('Regla: add_fondo arg list')
        pass

    @_('empty')
    def add_fondo_arg(self, _):
        self.semantics.operators_stack.append('(')
        if DEBUG_PARSER:
            print('Regla: add_fondo arg')
        pass

    @_('empty')
    def remove_fondo_arg(self, _):
        self.semantics.operators_stack.pop()
        if DEBUG_PARSER:
            print('Regla: add_fondo arg')
        pass

    # ASIGNACIÓN
    @_('ID ASSIGN expresion')
    def asignacion(self, p):
        if DEBUG_PARSER:
            print('Regla: asignacion')
        self.semantics.generate_quad_assign(name_var=p.ID)
        pass

    @_('array_usage ASSIGN expresion')
    def asignacion(self, p):
        if DEBUG_PARSER:
            print('Regla: asignacion')
        self.semantics.generate_quad_assign(array=True)
        pass

    # ESTATUTOS CONDICIONALES
    @_('start_if bloque condicion1')
    def condicion(self, p):
        self.semantics.end_if()
        if DEBUG_PARSER:
            print('Regla: condicion')
        pass

    @_('IF "(" expresiones ")"')
    def start_if(self, p):
        self.semantics.start_if()
        if DEBUG_PARSER:
            print('Regla: condicion')
        pass

    @_('inicio_else bloque', 'empty')
    def condicion1(self, p):
        if DEBUG_PARSER:
            print('Regla: condicion1')
        pass

    @_('ELSE')
    def inicio_else(self, p):
        self.semantics.start_else()
        if DEBUG_PARSER:
            print('Regla: condicion1')
        pass

    # LECTURA
    @_('READ "(" ID ")"')
    def lectura(self, p):
        self.semantics.generar_lectura(p.ID)
        if DEBUG_PARSER:
            print('Regla: lectura')
        pass

    # ESCRITURA
    @_('WRITE "(" constante ")"')
    def escritura(self, p):
        self.semantics.generar_escritura()
        if DEBUG_PARSER:
            print('Regla: escritura')
        pass

    @_('WRITE "(" call_fun_no_void ")"')
    def escritura(self, p):
        self.semantics.generar_escritura()
        if DEBUG_PARSER:
            print('Regla: escritura')
        pass

    # CICLOS CONDICIONALES
    # FOR
    @_('inicio_for initial_value_for end_value_for bloque')
    def ciclo_for(self, p):
        self.semantics.end_for()
        if DEBUG_PARSER:
            print('Regla: ciclo_for')
        pass

    @_('FOR ID')
    def inicio_for(self, p):
        self.semantics.start_for(p.ID)
        if DEBUG_PARSER:
            print('Regla: inicio_for')
        pass

    @_('ASSIGN exp')
    def initial_value_for(self, _):
        self.semantics.valor_inicial_for()
        if DEBUG_PARSER:
            print('Regla: valor_inicial_for')
        pass

    @_('TO exp')
    def end_value_for(self, _):
        self.semantics.valor_final_for()
        if DEBUG_PARSER:
            print('Regla: valor_final_for')
        pass

    # WHILE
    @_('inicio_while expresion_while bloque')
    def ciclo_while(self, _):
        self.semantics.end_while()
        if DEBUG_PARSER:
            print('Regla: ciclo_while')
        pass

    @_('WHILE')
    def inicio_while(self, _):
        self.semantics.start_while()
        if DEBUG_PARSER:
            print('Regla: inicio_while')
        pass

    @_('"(" expresiones ")"')
    def expresion_while(self, _):
        self.semantics.expresion_while()
        if DEBUG_PARSER:
            print('Regla: expresion_while')
        pass

    # EXPRESIONES
    @_('expresion expresiones1')
    def expresiones(self, _):
        if DEBUG_PARSER:
            print('Regla: expresiones')
        if self.semantics.operators_stack and self.semantics.operators_stack[-1] in ['&&', '||']:
            self.semantics.generate_quad()
        pass

    @_('AND expresiones', 'OR expresiones')
    def expresiones1(self, p):
        if DEBUG_PARSER:
            print('Regla: expresiones1')
        self.semantics.operators_stack.append(p[0])
        pass

    @_('empty')
    def expresiones1(self, _):
        if DEBUG_PARSER:
            print('Regla: expresiones1')
        pass

    # EXPRESION
    @_('exp expresion1')
    def expresion(self, _):
        if DEBUG_PARSER:
            print('Regla: expresion')
        pass

    @_('expresion2 exp')
    def expresion1(self, _):
        if DEBUG_PARSER:
            print('Regla: expresion1')
        if self.semantics.operators_stack[-1] in ['<=', '>=', '>', '<', '!=', '==']:
            self.semantics.generate_quad()
        pass

    @_('empty')
    def expresion1(self, _):
        if DEBUG_PARSER:
            print('Regla: expresion1')
        pass

    @_('LTEQ', 'GTEQ', 'GT', 'LT', 'NE', 'EQ')
    def expresion2(self, p):
        if DEBUG_PARSER:
            print('Regla: expresion2')
        self.semantics.operators_stack.append(p[0])
        pass

    # EXP
    @_('termino exp1')
    def exp(self, _):
        if DEBUG_PARSER:
            print('Regla: exp')
        if self.semantics.operators_stack and self.semantics.operators_stack[-1] in ['+', '-']:
            self.semantics.generate_quad()
        pass

    @_('exp2 exp', 'empty')
    def exp1(self, _):
        if DEBUG_PARSER:
            print('Regla: exp1')
        pass

    @_('"+"', '"-"')
    def exp2(self, p):
        if DEBUG_PARSER:
            print('Regla: exp2')
        self.semantics.operators_stack.append(p[0])
        pass

    # TERMINO
    @_('factor termino1')
    def termino(self, _):
        if DEBUG_PARSER:
            print('Regla: termino')
        if self.semantics.operators_stack and self.semantics.operators_stack[-1] in ['*', '/']:
            self.semantics.generate_quad()
        pass

    @_('termino2 termino')
    def termino1(self, _):
        if DEBUG_PARSER:
            print('Regla: termino1')
        pass

    @_('empty')
    def termino1(self, _):
        if DEBUG_PARSER:
            print('Regla: termino1')
        pass

    @_('"*"', '"/"')
    def termino2(self, p):
        if DEBUG_PARSER:
            print('Regla: termino2')
        self.semantics.operators_stack.append(p[0])
        pass
    
    # FACTOR
    @_('add_par exp ")"')
    def factor(self, _):
        if DEBUG_PARSER:
            print('Regla: factor')
        self.semantics.operators_stack.pop()
        pass

    @_('"("')
    def add_par(self, p):
        if DEBUG_PARSER:
            print('Regla: add_par')
        self.semantics.operators_stack.append(p[0])
        pass

    @_('constante')
    def factor(self, _):
        if DEBUG_PARSER:
            print('Regla: factor constante')
        pass

    @_('call_fun_no_void')
    def factor(self, _):
        if DEBUG_PARSER:
            print('Regla: factor call_fun_no_void')
        pass

    # CONSTANTE
    @_('ID')
    def constante(self, p):
        self.semantics.push_var_operand(p[0])
        if DEBUG_PARSER:
            print('Regla: constante id ' + p[0])
        pass

    @_('CTE_I')
    def constante(self, p):
        if DEBUG_PARSER:
            print('Regla: constante int ' + str(p[0]))
        self.semantics.push_const_operand(p[0], VarType.INT)
        pass

    @_('CTE_F')
    def constante(self, p):
        if DEBUG_PARSER:
            print('Regla: constante float ' + str(p[0]))
        self.semantics.push_const_operand(p[0], VarType.FLOAT)
        pass

    @_('CTE_S', 'CTE_C')
    def constante(self, p):
        if DEBUG_PARSER:
            print('Regla: constante char ' + str(p[0]))
        self.semantics.push_const_operand(p[0], VarType.CHAR)
        pass

    @_('array_usage')
    def constante(self, _):
        if DEBUG_PARSER:
            print('Regla: constante array_usage')
        pass

    # Operaciones con ARREGLOS
    # DECLARACION
    @_('"[" CTE_I "]"')
    def array_dec(self, p):
        if DEBUG_PARSER:
            print('Regla: array_dec 1 dim')
        return [p[1]]

    @_('"[" CTE_I "]" "[" CTE_I "]"')
    def array_dec(self, p):
        if DEBUG_PARSER:
            print('Regla: array_dec 2 dims')
        return [p[1], p[4]]

    @_('empty')
    def array_dec(self, _):
        if DEBUG_PARSER:
            print('Regla: array_dec empty')
        return []

    # USAGE
    @_('ID add_fondo exp remove_fondo')
    def array_usage(self, p):
        self.semantics.array_usage(p.ID, 1)
        if DEBUG_PARSER:
            print('Regla: array_usage 1 dimension')
        pass

    @_('ID add_fondo exp remove_fondo add_fondo exp remove_fondo')
    def array_usage(self, p):
        self.semantics.array_usage(p.ID, 2)
        if DEBUG_PARSER:
            print('Regla: array_usage 2 dimensiones')
        pass

    @_('"["')
    def add_fondo(self, _):
        self.semantics.operators_stack.append('(')
        if DEBUG_PARSER:
            print('Regla: add_fondo')
        pass

    @_('"]"')
    def remove_fondo(self, _):
        self.semantics.operators_stack.pop()
        if DEBUG_PARSER:
            print('Regla: add_fondo')
        pass

    @_('')
    def empty(self, _):
        if DEBUG_PARSER:
            print('Regla: Empty')
        pass

    def error(self, p):
        if p:
            raise Exception("Syntactical ERROR! Error at token " + str(p.type) + " in line " + str(p.lineno))
            # self.errok()
        else:
            raise Exception("Syntactical ERROR! Error at EOF")
