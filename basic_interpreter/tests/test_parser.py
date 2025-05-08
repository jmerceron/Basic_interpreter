import pytest
from ..lexer import Lexer
from ..parser import (
    Parser, NumberNode, StringNode, BinOpNode, PrintNode, VariableNode, 
    AssignNode, InputNode, IfNode, ForNode, GotoNode, UnaryOpNode
)

def parse_code(code: str):
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()

def test_number_expression():
    ast = parse_code("42")
    assert len(ast) == 1
    assert isinstance(ast[0], NumberNode)
    assert float(ast[0].token.value) == 42

def test_string_expression():
    ast = parse_code('"Hello"')
    assert len(ast) == 1
    assert isinstance(ast[0], StringNode)
    assert ast[0].token.value == "Hello"

def test_binary_operation():
    ast = parse_code("2 + 3")
    assert len(ast) == 1
    assert isinstance(ast[0], BinOpNode)
    assert isinstance(ast[0].left, NumberNode)
    assert isinstance(ast[0].right, NumberNode)
    assert ast[0].op_token.value == "+"

def test_print_statement():
    ast = parse_code('PRINT "Hello"')
    assert len(ast) == 1
    assert isinstance(ast[0], PrintNode)
    assert len(ast[0].expressions) == 1
    assert isinstance(ast[0].expressions[0], StringNode)

def test_let_statement():
    ast = parse_code('LET X = 42')
    assert len(ast) == 1
    assert isinstance(ast[0], AssignNode)
    assert ast[0].name == "X"
    assert isinstance(ast[0].value, NumberNode)

def test_complex_expression():
    ast = parse_code('LET Y = 10 * (5 + 3)')
    assert len(ast) == 1
    assert isinstance(ast[0], AssignNode)
    assert ast[0].name == "Y"
    assert isinstance(ast[0].value, BinOpNode)
    assert ast[0].value.op_token.value == "*"

def test_print_multiple_expressions():
    ast = parse_code('PRINT "Result:", 2 + 2')
    assert len(ast) == 1
    assert isinstance(ast[0], PrintNode)
    assert len(ast[0].expressions) == 2
    assert isinstance(ast[0].expressions[0], StringNode)
    assert isinstance(ast[0].expressions[1], BinOpNode)

def test_input_statement():
    ast = parse_code('INPUT X')
    assert len(ast) == 1
    assert isinstance(ast[0], InputNode)
    assert len(ast[0].variables) == 1
    assert ast[0].variables[0] == "X"

    # Test multiple variables
    ast = parse_code('INPUT X, Y, Z')
    assert len(ast) == 1
    assert isinstance(ast[0], InputNode)
    assert len(ast[0].variables) == 3
    assert ast[0].variables == ["X", "Y", "Z"]

def test_if_statement():
    ast = parse_code('IF X > 10 THEN PRINT "Large"')
    assert len(ast) == 1
    assert isinstance(ast[0], IfNode)
    assert isinstance(ast[0].condition, BinOpNode)
    assert isinstance(ast[0].then_statement, PrintNode)

    # Test with different condition
    ast = parse_code('IF 5 = 5 THEN LET X = 1')
    assert len(ast) == 1
    assert isinstance(ast[0], IfNode)
    assert isinstance(ast[0].condition, BinOpNode)
    assert isinstance(ast[0].then_statement, AssignNode)

def test_for_loop():
    ast = parse_code('''
    FOR I = 1 TO 10
    PRINT I
    NEXT
    ''')
    assert len(ast) == 1
    assert isinstance(ast[0], ForNode)
    assert ast[0].variable == "I"
    assert isinstance(ast[0].start, NumberNode)
    assert isinstance(ast[0].end, NumberNode)
    assert ast[0].step is None
    assert len(ast[0].body) == 1
    assert isinstance(ast[0].body[0], PrintNode)

    # Test FOR loop with STEP
    ast = parse_code('''
    FOR X = 10 TO 0 STEP -2
    LET Y = X * 2
    NEXT
    ''')
    assert len(ast) == 1
    assert isinstance(ast[0], ForNode)
    assert ast[0].variable == "X"
    assert isinstance(ast[0].start, NumberNode)
    assert isinstance(ast[0].end, NumberNode)
    assert isinstance(ast[0].step, NumberNode)
    assert float(ast[0].step.token.value) == -2
    assert len(ast[0].body) == 1
    assert isinstance(ast[0].body[0], AssignNode)

def test_goto_statement():
    ast = parse_code('GOTO 100')
    assert len(ast) == 1
    assert isinstance(ast[0], GotoNode)
    assert ast[0].line_number == 100

def test_unary_operations():
    ast = parse_code('-42')
    assert len(ast) == 1
    assert isinstance(ast[0], UnaryOpNode)
    assert ast[0].op_token.value == '-'
    assert isinstance(ast[0].expr, NumberNode)
    
    ast = parse_code('+42')
    assert len(ast) == 1
    assert isinstance(ast[0], UnaryOpNode)
    assert ast[0].op_token.value == '+'
    assert isinstance(ast[0].expr, NumberNode)

def test_multiple_statements():
    ast = parse_code('''
    LET X = 10
    PRINT X
    IF X > 5 THEN PRINT "Large"
    ''')
    assert len(ast) == 3
    assert isinstance(ast[0], AssignNode)
    assert isinstance(ast[1], PrintNode)
    assert isinstance(ast[2], IfNode)