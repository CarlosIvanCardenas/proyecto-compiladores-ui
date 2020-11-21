from compiler.lexer import CompLexer
from compiler.parser import CompParser
from compiler.output import CompilerOutput
from vm.vm import VM
from common.debug_flags import DEBUG_UI, DEBUG_LEXER, DEBUG_SEMANTIC
import sys

def main():
    if DEBUG_UI:
        # Lee código como un argumento del sistema
        code = sys.argv[1]
    else:
        # Lee codigo desde un archivo especificado
        input_file = open("examples/fibonacci_recursive.txt", "r")
        #input_file = open("examples/test_success3.txt", "r")
        code = input_file.read()
        input_file.close()

    # LEXER: Lexical Analysis
    lexer = CompLexer()
    for tok in lexer.tokenize(code):
        if not DEBUG_UI and DEBUG_LEXER:
            print('type=%r, value=%r' % (tok.type, tok.value))

    # PARSER: Syntactic Analysis
    parser = CompParser()
    compiler_output: CompilerOutput
    compiler_output = parser.parse(lexer.tokenize(code))

    # SEMANTICS
    if DEBUG_SEMANTIC:
        print('Quads: ')
        for i, quad in enumerate(compiler_output.quadruples):
            print(f'{i}.\t{quad.operator}\tA:{quad.left_operand}\tB:{quad.right_operand}\tC:{quad.result}')

    # VIRTUAL MACHINE
    vm = VM(quad_list=compiler_output.quadruples,
            const_table=compiler_output.constants,
            fun_dir=compiler_output.functions_directory)
    vm.run()


if __name__ == '__main__':
    main()
