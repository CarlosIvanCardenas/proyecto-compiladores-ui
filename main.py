from compiler.lexer import CompLexer
from compiler.parser import CompParser

def main():
    input_file = open("examples/fun_declaration_and_call", "r")
    input_text = input_file.read()
    print(input_text)

    # LEXER: Lexical Analysis
    print('\n\nLEXER Analysis:')
    lexer = CompLexer()
    for tok in lexer.tokenize(input_text):
        print('type=%r, value=%r' % (tok.type, tok.value))

    # PARSER: Syntactic Analysis
    print('\n\nPARSER Analysis:')
    parser = CompParser()
    result = parser.parse(lexer.tokenize(input_text))
    print(result)

    input_file.close()


if __name__ == '__main__':
    main()
