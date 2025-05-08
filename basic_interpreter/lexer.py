from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    KEYWORD = auto()
    OPERATOR = auto()
    EOL = auto()
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class Lexer:
    KEYWORDS = {
        'PRINT', 'INPUT', 'LET', 'GOTO', 'IF', 'THEN', 'FOR', 'NEXT',
        'TO', 'STEP', 'END', 'STOP', 'DEF', 'GOSUB', 'RETURN', 'DIM',
        'REM', 'RANDOM', 'RND'
    }

    COMPOUND_OPERATORS = {
        '<': ['<=', '<>', '<'],
        '>': ['>=', '>'],
        '=': ['=']
    }

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None
        self.line = 1
        self.column = 1

    def error(self):
        raise Exception(f'Invalid character at line {self.line}, column {self.column}')

    def advance(self):
        self.pos += 1
        self.column += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def peek(self):
        peek_pos = self.pos + 1
        return self.text[peek_pos] if peek_pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace() and self.current_char != '\n':
            self.advance()

    def skip_comment(self):
        while self.current_char and self.current_char != '\n':
            self.advance()

    def number(self):
        result = ''
        start_column = self.column

        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()

        try:
            return Token(TokenType.NUMBER, float(result), self.line, start_column)
        except ValueError:
            self.error()

    def string(self):
        result = ''
        start_column = self.column
        self.advance()  # Skip opening quote

        while self.current_char and self.current_char != '"':
            result += self.current_char
            self.advance()

        if self.current_char == '"':
            self.advance()  # Skip closing quote
            return Token(TokenType.STRING, result, self.line, start_column)
        else:
            self.error()

    def identifier(self):
        result = ''
        start_column = self.column

        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        token_type = TokenType.KEYWORD if result.upper() in self.KEYWORDS else TokenType.IDENTIFIER
        return Token(token_type, result.upper(), self.line, start_column)

    def handle_operator(self) -> Token:
        start_char = self.current_char
        column = self.column
        
        if start_char in self.COMPOUND_OPERATORS:
            current = start_char
            self.advance()
            
            # Try to form a compound operator
            if self.current_char:
                potential = current + self.current_char
                for op in self.COMPOUND_OPERATORS[start_char]:
                    if op == potential:
                        self.advance()
                        return Token(TokenType.OPERATOR, op, self.line, column)
            
            # If no compound operator matches, return the single char operator
            return Token(TokenType.OPERATOR, current, self.line, column)
        else:
            # Handle single-char operators
            self.advance()
            return Token(TokenType.OPERATOR, start_char, self.line, column)

    def get_next_token(self):
        while self.current_char:
            # Skip whitespace
            if self.current_char.isspace() and self.current_char != '\n':
                self.skip_whitespace()
                continue

            # Handle new lines
            if self.current_char == '\n':
                self.line += 1
                self.column = 0
                self.advance()
                return Token(TokenType.EOL, '\n', self.line - 1, self.column)

            # Handle numbers
            if self.current_char.isdigit():
                return self.number()

            # Handle strings
            if self.current_char == '"':
                return self.string()

            # Handle identifiers and keywords
            if self.current_char.isalpha():
                return self.identifier()

            # Handle comments
            if self.current_char == "'" or (self.current_char == 'R' and self.peek() == 'E'):
                self.skip_comment()
                continue

            # Handle operators
            if self.current_char in '+-*/()=<>,:;':
                return self.handle_operator()

            self.error()

        return Token(TokenType.EOF, '', self.line, self.column)

    def tokenize(self):
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens