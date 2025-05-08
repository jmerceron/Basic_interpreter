import pytest
from ..lexer import Lexer, TokenType

def test_number_tokens():
    lexer = Lexer("42 3.14")
    tokens = lexer.tokenize()
    assert len(tokens) == 3  # Two numbers and EOF
    assert tokens[0].type == TokenType.NUMBER
    assert float(tokens[0].value) == 42
    assert tokens[1].type == TokenType.NUMBER
    assert float(tokens[1].value) == 3.14

def test_string_tokens():
    lexer = Lexer('"Hello, World!"')
    tokens = lexer.tokenize()
    assert len(tokens) == 2  # String and EOF
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "Hello, World!"

def test_keywords():
    lexer = Lexer("PRINT LET IF THEN")
    tokens = lexer.tokenize()
    assert len(tokens) == 5  # Four keywords and EOF
    for token in tokens[:-1]:  # Exclude EOF
        assert token.type == TokenType.KEYWORD

def test_operators():
    lexer = Lexer("+ - * / = < > <= >= <>")
    tokens = lexer.tokenize()
    assert len(tokens) == 11  # Ten operators and EOF
    for token in tokens[:-1]:  # Exclude EOF
        assert token.type == TokenType.OPERATOR

def test_basic_program():
    program = '''
    LET X = 10
    PRINT "Value:", X
    IF X > 5 THEN PRINT "Greater than 5"
    '''
    lexer = Lexer(program)
    tokens = lexer.tokenize()
    # Filter out EOL and EOF tokens for this test
    tokens = [t for t in tokens if t.type not in (TokenType.EOL, TokenType.EOF)]
    
    expected_types = [
        TokenType.KEYWORD,  # LET
        TokenType.IDENTIFIER,  # X
        TokenType.OPERATOR,  # =
        TokenType.NUMBER,  # 10
        TokenType.KEYWORD,  # PRINT
        TokenType.STRING,  # "Value:"
        TokenType.OPERATOR,  # ,
        TokenType.IDENTIFIER,  # X
        TokenType.KEYWORD,  # IF
        TokenType.IDENTIFIER,  # X
        TokenType.OPERATOR,  # >
        TokenType.NUMBER,  # 5
        TokenType.KEYWORD,  # THEN
        TokenType.KEYWORD,  # PRINT
        TokenType.STRING,  # "Greater than 5"
    ]
    
    assert len(tokens) == len(expected_types)
    for token, expected_type in zip(tokens, expected_types):
        assert token.type == expected_type