import ply.lex as lex
import ply.yacc as yacc
import argparse
from AbstractSyntaxTree import Node

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True, help='path to input source file of simple language')
opt = parser.parse_args()
print(opt)

# perform lexical analysis

# define a list of tokens
# define a list of reserved words
reserved = ['and', 'array', 'begin', 'bool', 'call', 'case', 'char', 'constant', 'do', 'else', 'end', 'false', 'for',
            'if', 'input', 'integer', 'not', 'of', 'or', 'output', 'procedure', 'program', 'read', 'real', 'repeat',
            'set', 'then', 'to', 'true', 'until', 'var', 'while', 'write', ]
reserved = {word: word.upper() for word in reserved}

# define a list of other tokens
tokens = [
    'NUMBER',
    'ID',
    'NEQ',  # <>
    'LE',  # <=
    'GE',  # >=
    'ASSIGNMENT',  # :=, handled
    'COMMENT',
    'ELLIPSIS',  # ..
    'STRING_LITERAL',
]

# merge the two together
tokens = tokens + list(reserved.values())

# define literals
literals = "+-*/=<>()[]:.;,'_"

# define a series of regex for each type of token
t_STRING_LITERAL = r"\'.*\'"
t_NEQ = r'<>'
t_LE = r'<='
t_GE = r'>='
t_ASSIGNMENT = r':='
t_ELLIPSIS = r'\.\.'


def t_COMMENT(t):
    r'\/\*.*\*\/'
    pass  # returns nothing since comments do not go through compiler


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_ID(t):  # the underscore is added for purpose of generality
    r'[a-zA-Z_][a-zA-z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t


# define ignore characters, newline handling, error handling, etc.
t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# instantiate a lex object, named lexer
lexer = lex.lex(debug=1)

# feed input to lexer
with open(opt.input) as f:
    lexer.input(f.read())

# get a list of all tokens returned by lexer.token() and the symbol table
toks = list(lexer)
symbols = set(tok.value for tok in toks if tok.type == "ID")


# TODO perform syntactic analysis

# 0
def p_empty(p):
    """ empty : """
    p[0] = None


# 8
def p_identifier(p):
    """ identifier : ID """
    p[0] = Node(type="identifier", leaf=p[1])


# 9
def p_constant(p):
    """  constant : integer
                  | boolean_constant
                  | character_constant
                  | constant_identifier
                  | real_number """
    p[0] = Node(type="constant", children=[p[1]])


# 10
def p_integer(p):
    """ integer : NUMBER """
    p[0] = Node(type="integer", leaf=p[1])


# 11
def p_boolean_constant(p):
    """  boolean_constant : TRUE
                          | FALSE """
    p[0] = Node(type='boolean_constant', leaf=p[1])


# 12
def p_character_constant(p):
    """  character_constant : STRING_LITERAL """
    p[0] = Node(type="character_constant", leaf=p[1])


# 13
def p_constant_identifier(p):
    """  constant_identifier : identifier """
    p[0] = Node(type='constant_identifier', children=[p[1]])


# 14
def p_real_number(p):
    """  real_number : integer '.' integer """
    p[0] = Node(type='real_number', children=[p[1], p[3]], leaf=p[2])


# 15
def p_type(p):
    """  type : simple_type
              | compound_type """
    p[0] = Node(type='type', children=[p[1]])


# 16
def p_simple_type(p):
    """  simple_type : INTEGER
                     | BOOL
                     | CHAR
                     | REAL """
    p[0] = Node(type='simple_type', leaf=p[1])


# 17
def p_compound_type(p):
    """  compound_type : ARRAY '[' index ']' OF simple_type """
    p[0] = Node(type='compound_type', children=[p[3], p[6]], leaf=[p[1], p[2], p[4], p[5]])


# 18
def p_index(p):
    """  index : integer
               | integer ELLIPSIS integer
               | index ',' integer
               | index ',' integer ELLIPSIS integer """

    if len(p) == 2:
        p[0] = Node(type='index', children=[p[1]])
    elif len(p) == 4:
        p[0] = Node(type="index", children=[p[1], p[3]], leaf=p[2])
    else:
        p[0] = Node(type="index", children=[p[1], p[3], p[5]], leaf=[p[2], p[4]])


# 19
def p_expression(p):
    """  expression : arithmetic_expression
                    | boolean_expression
                    | character_expression """
    p[0] = Node(type='expression', leaf=p[1])


# 20
def p_arithmetic_expression(p):
    """  arithmetic_expression : arithmetic_expression '+' term
                               | arithmetic_expression '-' term
                               | '+' term
                               | '-' term
                               | term """
    if len(p) == 2:
        p[0] = Node(type='arithmetic_expression', children=[p[1]])
    elif len(p) == 3:
        p[0] = Node(type='arithmetic_expression', children=[p[2]], leaf=p[1])
    else:
        p[0] = Node(type='arithmetic_expression', children=[p[1], p[3]], leaf=p[2])


# 21
def p_term(p):
    """  term : term '*' factor
              | term '/' factor
              | factor """
    if len(p) == 2:
        p[0] = Node(type='term', children=[p[1]])
    else:
        p[0] = Node(type='term', children=[p[1], p[3]], leaf=p[2])


# 22
def p_factor(p):
    """  factor : arithmetic_value
                | '(' arithmetic_expression ')' """
    if len(p) == 2:
        p[0] = Node(type='factor', children=[p[1]])
    else:
        p[0] = Node(type='factor', children=[p[2]], leaf=[p[1], p[3]])


# 23
def p_arithmetic_value(p):
    """  arithmetic_value : identifier
                          | integer """
    p[0] = Node(type='arithmetic_value', children=[p[1]])


# 24
def p_boolean_expression(p):
    """  boolean_expression : boolean_expression OR boolean_term
                            | boolean_term """
    if len(p) == 2:
        p[0] = Node(type='boolean_expression', children=[p[1]])
    else:
        p[0] = Node(type='boolean_expression', children=[p[1], p[3]], leaf=p[2])


# 25
def p_boolean_term(p):
    """  boolean_term : boolean_term AND boolean_factor
                      | boolean_factor """
    if len(p) == 2:
        p[0] = Node(type='boolean_term', children=[p[1]])
    else:
        p[0] = Node(type='boolean_term', children=[p[1], p[3]], leaf=p[2])


# 26
def p_boolean_factor(p):
    """  boolean_factor : boolean_value
                        | NOT boolean_factor """
    if len(p) == 2:
        p[0] = Node(type='boolean_factor', children=[p[1]])
    else:
        p[0] = Node(type='boolean_factor', children=[p[2]], leaf=p[1])


# 27
def p_boolean_value(p):
    """  boolean_value : boolean_constant
                       | identifier
                       | '(' boolean_expression ')' identifier  relation_symbol  identifier
                       | '(' arithmetic_expression ')' relation_symbol  '(' arithmetic_expression ')' """
    if len(p) == 2:
        p[0] = Node(type='boolean_value', children=[p[1]])
    elif len(p) == 7:
        p[0] = Node(type='boolean_value', children=[p[2], p[4], p[5], p[6]], leaf=[p[1], p[3]])
    else:
        p[0] = Node(type="boolean_value", children=[p[2], p[4], p[6]], leaf=[p[1], p[3], p[5], p[7]])


# 28
def p_character_expression(p):
    """  character_expression : character_value """
    p[0] = Node(type='character_expression', children=[p[1]])


# 29
def p_character_value(p):
    """  character_value : character_constant
                         | identifier """
    p[0] = Node(type='character_value', children=[p[1]])


# 30
# TODO change the following docstring to standard format
def p_relation_symbol(p):
    """  relation_symbol : '<'
                         | NEQ
                         | LE
                         | GE
                         | '>'
                         | '=' """
    p[0] = Node(type='relation_symbol', leaf=p[1])


# 31
def p_clause(p):
    """  clause : declaration_clause
                | execution_clause """
    p[0] = Node(type='clause', children=[p[1]])


# 32
def p_declaration_clause(p):
    """  declaration_clause : constant_declaration
                            | variable_declaration
                            | procedure_declaration """
    p[0] = Node(type='declaration_clause', children=[p[1]])


# 33
def p_constant_declaration(p):
    """  constant_declaration : CONSTANT constant_definition
                              | empty """
    if len(p) == 2:
        p[0] = Node(type='constant_declaration', children=[p[1]])
    else:
        p[0] = Node(type='constant_declaration', children=[p[2]], leaf=p[1])


# 34
def p_constant_definition(p):
    """  constant_definition : identifier '=' constant ';' constant_definition
                             | identifier '=' constant ';' """
    if len(p) == 6:
        p[0] = Node(type='constant_definition', children=[p[1], p[3], p[5]], leaf=[p[2], p[4]])
    else:
        p[0] = Node(type='constant_definition', children=[p[1], p[3]], leaf=[p[2], p[4]])


# 35
def p_variable_declaration(p):
    """  variable_declaration : VAR variable_definition
                              | empty """
    if len(p) == 2:
        p[0] = Node(type='variable_declaration', children=p[1])
    else:
        p[0] = Node(type='variable_declaration', children=[p[2]], leaf=p[1])


# 36
def p_variable_definition(p):
    """  variable_definition : identifier_table ':' type ';'
                             | identifier_table ':' type ';' variable_definition """
    if len(p) == 5:
        p[0] = Node(type='variable_definition', children=[p[1], p[3]], leaf=[p[2], p[4]])
    else:
        p[0] = Node(type='variable_definition', children=[p[1], p[3], p[5]], leaf=[p[2], p[4]])


# 37
def p_identifier_table(p):
    """  identifier_table : identifier ',' identifier_table
                          | identifier """
    if len(p) == 2:
        p[0] = Node(type='identifier_table', children=[p[1]])
    else:
        p[0] = Node(type='identifier_table', children=[p[1], p[3]], leaf=p[2])


# 38
def p_execution_clause(p):
    """  execution_clause : simple_clause
                          | structured_clause """
    p[0] = Node(type='execution_clause', children=[p[1]])


# 39
def p_simple_clause(p):
    """  simple_clause : assignment
                       | calling
                       | read_clause
                       | write_clause """
    p[0] = Node(type='simple_clause', children=[p[1]])


# 40
def p_assignment(p):
    """  assignment : variable ASSIGNMENT expression """
    p[0] = Node(type='assignment', children=[p[1], p[3]], leaf=p[2])


# 41
def p_variable(p):
    """  variable : single_variable
                  | index_variable """
    p[0] = Node(type='variable', children=[p[1]])


# 42
def p_single_variable(p):
    """  single_variable : identifier """
    p[0] = Node(type='single_variable', children=[p[1]])


# 43
def p_index_variable(p):
    """  index_variable : identifier '[' expression_table ']' """
    p[0] = Node(type='index_variable', children=[p[1], p[3]], leaf=[p[2], p[4]])


# 44
def p_expression_table(p):
    """  expression_table : expression ',' expression_table
                          | expression """
    if len(p) == 2:
        p[0] = Node(type='expression_table', children=[p[1]])
    else:
        p[0] = Node(type='expression_table', children=[p[1], p[3]], leaf=p[2])


# 45
def p_calling(p):
    """  calling : CALL identifier  '(' real_parameter_table ')' """
    p[0] = Node(type='calling', children=[p[2], p[4]], leaf=[p[1], p[3], p[5]])


# 46
def p_real_parameter_table(p):
    """  real_parameter_table : expression ',' real_parameter_table
                              | expression """
    if len(p) == 2:
        p[0] = Node(type='real_parameter_table', children=[p[1]])
    else:
        p[0] = Node(type='real_parameter_table', children=[p[1], p[3]], leaf=p[2])


# 47
def p_read_clause(p):
    """  read_clause : READ '(' input_variable_table ')' """
    p[0] = Node(type='read_clause', children=[p[3]], leaf=[p[1], p[2], p[4]])


# 48
def p_input_variable_table(p):
    """  input_variable_table : variable
                              | variable ',' input_variable_table """
    if len(p) == 2:
        p[0] = Node(type='input_variable_table', children=[p[1]])
    else:
        p[0] = Node(type='input_variable_table', children=[p[1], p[3]], leaf=p[2])


# 49
def p_write_clause(p):
    """  write_clause : WRITE '(' expression_table ')' """
    p[0] = Node(type='write_clause', children=[p[3]], leaf=[p[1], p[2], p[4]])


# 50
def p_structured_clause(p):
    """  structured_clause : compound_clause
                           | if_clause
                           | while_clause
                           | for_clause
                           | repeat_clause """
    p[0] = Node(type='structured_clause', children=[p[1]])


# 51
def p_compound_clause(p):
    """  compound_clause : BEGIN clause_table END """
    p[0] = Node(type='compound_clause', children=[p[2]], leaf=[p[1], p[3]])


# 52
def p_clause_table(p):
    """  clause_table : execution_clause ';' clause_table
                      | execution_clause """
    if len(p) == 2:
        p[0] = Node(type='clause_table', children=[p[1]])
    else:
        p[0] = Node(type='clause_table', children=[p[1], p[3]], leaf=p[2])


# 53
def p_if_clause(p):
    """  if_clause : IF boolean_expression THEN execution_clause
                   | IF boolean_expression THEN execution_clause ELSE execution_clause """
    if len(p) == 5:
        p[0] = Node(type='if_clause', children=[p[2], p[4]], leaf=[p[1], p[3]])
    else:
        p[0] = Node(type='if_clause', children=[p[2], p[4], p[6]], leaf=[p[1], p[3], p[5]])


# 54
def p_while_clause(p):
    """  while_clause : WHILE boolean_expression DO execution_clause """
    p[0] = Node(type='while_clause', children=[p[2], p[4]], leaf=[p[1], p[3]])


# 55
def p_repeat_clause(p):
    """  repeat_clause : REPEAT execution_clause UNTIL boolean_expression """
    p[0] = Node(type='repeat_clause', children=[p[2], p[4]], leaf=[p[1], p[3]])


# 56
def p_for_clause(p):
    """  for_clause : FOR variable ASSIGNMENT expression TO expression DO execution_clause """
    p[0] = Node(type='for_clause', children=[p[2], p[4], p[6], p[8]], leaf=[p[1], p[3], p[5], p[7]])


# 57
def p_procedure_declaration(p):
    """  procedure_declaration : PROCEDURE identifier  '(' formal_parameter_table ')' subroutine
                               | empty """
    if len(p) == 2:
        p[0] = Node(type='procedure_declaration', children=[p[1]])
    else:
        p[0] = Node(type='procedure_declaration', children=[p[2], p[4], p[6]], leaf=[p[1], p[3], p[5]])


# 58
def p_formal_parameter_table(p):
    """  formal_parameter_table : variable ':' simple_type
                                | variable ':' simple_type ',' formal_parameter_table """
    if len(p) == 4:
        p[0] = Node(type='formal_parameter_table', children=[p[1], p[3]], leaf=p[2])
    else:
        p[0] = Node(type='formal_parameter_table', children=[p[1], p[3], p[5]], leaf=[p[2], p[4]])


# 59
def p_subroutine(p):
    """  subroutine : constant_declaration  variable_declaration  procedure_declaration  compound_clause """
    p[0] = Node(type='subroutine', children=[p[1], p[2], p[3], p[4]])


# 60
def p_program(p):
    """  program : PROGRAM identifier  subroutine """
    p[0] = Node(type='program', children=[p[2], p[3]], leaf=p[1])


def p_error(p):
    print("Error at token", p, "detected")


parser = yacc.yacc(debug=1, start='program')

with open(opt.input) as f:
    # re-initialize the line number
    lexer.lineno = 1
    result = parser.parse(f.read())

if __name__ == "__main__":
    result.traverse()