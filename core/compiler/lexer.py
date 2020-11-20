from sly import Lexer as SlyLexer


class CompLexer(SlyLexer):
    # Set of token names
    tokens = {PROGRAM, ID, VAR, INT, FLOAT, CHAR, FUN, VOID, RETURN, MAIN, IF, ELSE, READ, WRITE, FOR, TO, WHILE,
              AND, OR, EQ, NE, LT, GT, ASSIGN, CTE_S, CTE_I, CTE_F, CTE_C}

    # Set of literal tokens
    literals = {'(', ')', '[', ']', '{', '}', ';', ':', ',', '+', '-', '*', '/'}

    # String containing ignored characters between tokens
    ignore = ' \t'

    # Regular expression rules for tokens
    AND = r'&&'
    OR = r'\|\|'
    EQ = r'=='
    ASSIGN = r'='
    NE = r'!='
    LT = r'<'
    GT = r'>'
    CTE_S = r'\".+\"'

    # Identifiers and keywords
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['program'] = PROGRAM
    ID['var'] = VAR
    ID['int'] = INT
    ID['float'] = FLOAT
    ID['char'] = CHAR
    ID['fun'] = FUN
    ID['void'] = VOID
    ID['return'] = RETURN
    ID['main'] = MAIN
    ID['if'] = IF
    ID['else'] = ELSE
    ID['read'] = READ
    ID['write'] = WRITE
    ID['for'] = FOR
    ID['to'] = TO
    ID['while'] = WHILE

    ignore_comment = r'\#.*'

    @_(r'\d+\.\d+')
    def CTE_F(self, t):
        t.value = float(t.value)
        return t

    @_(r'\d+')
    def CTE_I(self, t):
        t.value = int(t.value)
        return t

    @_(r'\'.\'')
    def CTE_C(self, t):
        t.value = "'" + t.value[1] + "'"
        return t

    # Line number tracking
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print('LEXICAL ERROR! Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1


Tokens = CompLexer.tokens
