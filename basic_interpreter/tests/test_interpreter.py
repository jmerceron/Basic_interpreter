import pytest
from io import StringIO
import sys
from ..lexer import Lexer
from ..parser import Parser
from ..interpreter import Interpreter

def run_basic(code: str, input_values=None):
    # Set up input simulation if provided
    if input_values:
        input_iter = iter(input_values)
        input_mock = lambda _: next(input_iter)
    else:
        input_mock = lambda _: ""

    # Capture stdout for testing
    stdout = StringIO()
    sys.stdout = stdout
    
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        # Set the mock input function
        interpreter.input_fn = input_mock
        interpreter.interpret(ast)
        
        return stdout.getvalue().strip()
    finally:
        sys.stdout = sys.__stdout__

def test_arithmetic():
    assert run_basic('PRINT 2 + 3 * 4') == '14'
    assert run_basic('PRINT 10 - 2 * 3') == '4'
    assert run_basic('PRINT (2 + 3) * 4') == '20'

def test_variables():
    program = '''
    LET X = 42
    PRINT X
    '''
    assert run_basic(program) == '42'

def test_string_operations():
    program = '''
    LET MSG = "Hello"
    PRINT MSG, "World!"
    '''
    assert run_basic(program) == 'Hello World!'

def test_input_statement():
    program = '''
    INPUT X
    PRINT "You entered:", X
    '''
    assert run_basic(program, ["42"]) == 'You entered: 42'

def test_if_statement():
    program = '''
    LET X = 10
    IF X > 5 THEN PRINT "Greater"
    IF X < 5 THEN PRINT "Lesser"
    '''
    assert run_basic(program) == 'Greater'

def test_for_loop():
    program = '''
    LET SUM = 0
    FOR I = 1 TO 5
    LET SUM = SUM + I
    NEXT
    PRINT SUM
    '''
    assert run_basic(program) == '15'

def test_complex_program():
    program = '''
    LET N = 5
    LET FACT = 1
    FOR I = 1 TO N
    LET FACT = FACT * I
    NEXT
    PRINT "Factorial of", N, "is:", FACT
    '''
    assert run_basic(program) == 'Factorial of 5 is: 120'