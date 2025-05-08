from typing import Any, Dict, List, Optional
from .parser import (
    ASTNode, NumberNode, StringNode, VariableNode, BinOpNode,
    UnaryOpNode, AssignNode, PrintNode, InputNode, IfNode,
    ForNode, GotoNode
)

class Interpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.program: List[ASTNode] = []
        self.current_line = 0
        self.input_fn = input  # Add configurable input function

    def format_value(self, value: Any) -> str:
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    def visit(self, node: ASTNode) -> Any:
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, None)
        if visitor is None:
            raise Exception(f'No visitor found for {type(node).__name__}')
        return visitor(node)

    def visit_NumberNode(self, node: NumberNode) -> float:
        return float(node.token.value)

    def visit_StringNode(self, node: StringNode) -> str:
        return str(node.token.value)

    def visit_VariableNode(self, node: VariableNode) -> Any:
        var_name = node.token.value
        if var_name not in self.variables:
            raise Exception(f'Undefined variable: {var_name}')
        return self.variables[var_name]

    def visit_BinOpNode(self, node: BinOpNode) -> float:
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        if node.op_token.value == '+':
            return left + right
        elif node.op_token.value == '-':
            return left - right
        elif node.op_token.value == '*':
            return left * right
        elif node.op_token.value == '/':
            if right == 0:
                raise Exception('Division by zero')
            return left / right
        elif node.op_token.value in ['<', '>', '=', '<=', '>=', '<>']:
            if node.op_token.value == '=':
                return float(left == right)
            elif node.op_token.value == '<':
                return float(left < right)
            elif node.op_token.value == '>':
                return float(left > right)
            elif node.op_token.value == '<=':
                return float(left <= right)
            elif node.op_token.value == '>=':
                return float(left >= right)
            elif node.op_token.value == '<>':
                return float(left != right)
        
        raise Exception(f'Unknown operator: {node.op_token.value}')

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> float:
        value = self.visit(node.expr)
        if node.op_token.value == '+':
            return value
        elif node.op_token.value == '-':
            return -value
        raise Exception(f'Unknown unary operator: {node.op_token.value}')

    def visit_AssignNode(self, node: AssignNode) -> None:
        self.variables[node.name] = self.visit(node.value)

    def visit_PrintNode(self, node: PrintNode) -> None:
        values = []
        for expr in node.expressions:
            value = self.visit(expr)
            values.append(self.format_value(value))
        print(' '.join(values))

    def visit_InputNode(self, node: InputNode) -> None:
        for var_name in node.variables:
            value = self.input_fn(f"Enter value for {var_name}: ")
            try:
                # Try to convert to float if possible
                self.variables[var_name] = float(value)
            except ValueError:
                # Otherwise store as string
                self.variables[var_name] = value

    def visit_IfNode(self, node: IfNode) -> None:
        condition = self.visit(node.condition)
        if condition:
            self.visit(node.then_statement)

    def visit_ForNode(self, node: ForNode) -> None:
        start_val = self.visit(node.start)
        end_val = self.visit(node.end)
        step_val = 1 if node.step is None else self.visit(node.step)
        
        self.variables[node.variable] = start_val
        
        while ((step_val > 0 and self.variables[node.variable] <= end_val) or
               (step_val < 0 and self.variables[node.variable] >= end_val)):
            for statement in node.body:
                self.visit(statement)
            self.variables[node.variable] += step_val

    def visit_GotoNode(self, node: GotoNode) -> None:
        self.current_line = node.line_number - 1  # Adjust for 0-based indexing

    def interpret(self, program: List[ASTNode]) -> None:
        self.program = program
        self.current_line = 0
        
        while self.current_line < len(self.program):
            node = self.program[self.current_line]
            self.visit(node)
            self.current_line += 1