from dataclasses import dataclass
from typing import List, Union, Optional
from .lexer import Token, TokenType

# AST Node classes
@dataclass
class NumberNode:
    token: Token

@dataclass
class StringNode:
    token: Token

@dataclass
class VariableNode:
    token: Token

@dataclass
class BinOpNode:
    left: 'ASTNode'
    op_token: Token
    right: 'ASTNode'

@dataclass
class UnaryOpNode:
    op_token: Token
    expr: 'ASTNode'

@dataclass
class AssignNode:
    name: str
    value: 'ASTNode'

@dataclass
class PrintNode:
    expressions: List['ASTNode']

@dataclass
class InputNode:
    variables: List[str]

@dataclass
class IfNode:
    condition: 'ASTNode'
    then_statement: 'ASTNode'

@dataclass
class ForNode:
    variable: str
    start: 'ASTNode'
    end: 'ASTNode'
    step: Optional['ASTNode']
    body: List['ASTNode']

@dataclass
class GotoNode:
    line_number: int

ASTNode = Union[NumberNode, StringNode, VariableNode, BinOpNode, UnaryOpNode,
                AssignNode, PrintNode, InputNode, IfNode, ForNode, GotoNode]

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None

    def error(self):
        raise Exception(f'Invalid syntax at {self.current_token}')

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def peek(self):
        peek_pos = self.pos + 1
        return self.tokens[peek_pos] if peek_pos < len(self.tokens) else None

    def match(self, type_: TokenType, value: str = None) -> bool:
        if self.current_token and self.current_token.type == type_:
            if value is None or self.current_token.value == value:
                self.advance()
                return True
        return False

    def expect(self, type_: TokenType, value: str = None):
        if not self.match(type_, value):
            self.error()

    def factor(self) -> ASTNode:
        token = self.current_token

        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(token)
        elif token.type == TokenType.STRING:
            self.advance()
            return StringNode(token)
        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            return VariableNode(token)
        elif token.type == TokenType.OPERATOR and token.value in ('+', '-'):
            self.advance()
            return UnaryOpNode(token, self.factor())
        elif token.value == '(':
            self.advance()
            expr = self.expr()
            self.expect(TokenType.OPERATOR, ')')
            return expr
        
        self.error()

    def term(self) -> ASTNode:
        node = self.factor()

        while self.current_token and self.current_token.type == TokenType.OPERATOR and \
              self.current_token.value in ('*', '/'):
            token = self.current_token
            self.advance()
            node = BinOpNode(node, token, self.factor())

        return node

    def expr(self) -> ASTNode:
        node = self.term()

        while self.current_token and self.current_token.type == TokenType.OPERATOR and \
              self.current_token.value in ('+', '-', '<', '>', '=', '<=', '>=', '<>'):
            token = self.current_token
            self.advance()
            node = BinOpNode(node, token, self.term())

        return node

    def expression_statement(self) -> ASTNode:
        """Handle standalone expressions like numbers, strings, or unary operations"""
        if self.current_token.type in (TokenType.NUMBER, TokenType.STRING) or \
           (self.current_token.type == TokenType.OPERATOR and self.current_token.value in ('+', '-')):
            return self.expr()
        self.error()

    def statement(self) -> Optional[ASTNode]:
        if not self.current_token:
            return None

        if self.current_token.type == TokenType.KEYWORD:
            if self.current_token.value == 'PRINT':
                return self.print_statement()
            elif self.current_token.value == 'LET':
                return self.let_statement()
            elif self.current_token.value == 'INPUT':
                return self.input_statement()
            elif self.current_token.value == 'IF':
                return self.if_statement()
            elif self.current_token.value == 'FOR':
                return self.for_statement()
            elif self.current_token.value == 'GOTO':
                return self.goto_statement()

        # Handle standalone expressions
        return self.expression_statement()

    def print_statement(self) -> PrintNode:
        self.expect(TokenType.KEYWORD, 'PRINT')
        expressions = [self.expr()]
        
        while self.current_token and self.current_token.value == ',':
            self.advance()
            expressions.append(self.expr())

        return PrintNode(expressions)

    def let_statement(self) -> AssignNode:
        self.expect(TokenType.KEYWORD, 'LET')
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error()
        
        var_name = self.current_token.value
        self.advance()
        self.expect(TokenType.OPERATOR, '=')
        value = self.expr()
        return AssignNode(var_name, value)

    def input_statement(self) -> InputNode:
        self.expect(TokenType.KEYWORD, 'INPUT')
        variables = []
        
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error()
            
        variables.append(self.current_token.value)
        self.advance()
        
        while self.current_token and self.current_token.value == ',':
            self.advance()
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error()
            variables.append(self.current_token.value)
            self.advance()
            
        return InputNode(variables)

    def if_statement(self) -> IfNode:
        self.expect(TokenType.KEYWORD, 'IF')
        condition = self.expr()  # This will now handle the relational operators
        self.expect(TokenType.KEYWORD, 'THEN')
        then_statement = self.statement()
        return IfNode(condition, then_statement)

    def number_from_unary(self, node: ASTNode) -> NumberNode:
        """Convert a UnaryOpNode with a NumberNode to a single NumberNode with the sign applied"""
        if isinstance(node, UnaryOpNode) and isinstance(node.expr, NumberNode):
            value = float(node.expr.token.value)
            if node.op_token.value == '-':
                value = -value
            return NumberNode(Token(TokenType.NUMBER, value, node.op_token.line, node.op_token.column))
        return node

    def for_statement(self) -> ForNode:
        self.expect(TokenType.KEYWORD, 'FOR')
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error()
            
        var_name = self.current_token.value
        self.advance()
        self.expect(TokenType.OPERATOR, '=')
        start = self.expr()
        self.expect(TokenType.KEYWORD, 'TO')
        end = self.expr()
        
        step = None
        if self.current_token and self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'STEP':
            self.advance()
            step = self.number_from_unary(self.expr())
            
        body = []
        while self.current_token and self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'NEXT':
                break
                
            if self.current_token.type == TokenType.EOL:
                self.advance()
                continue
                
            stmt = self.statement()
            if stmt:
                body.append(stmt)
                
        self.expect(TokenType.KEYWORD, 'NEXT')
        return ForNode(var_name, start, end, step, body)

    def goto_statement(self) -> GotoNode:
        self.expect(TokenType.KEYWORD, 'GOTO')
        if self.current_token.type != TokenType.NUMBER:
            self.error()
        line_number = int(self.current_token.value)
        self.advance()
        return GotoNode(line_number)

    def parse(self) -> List[ASTNode]:
        statements = []
        while self.current_token and self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.EOL:
                self.advance()
                continue
                
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
                
        return statements