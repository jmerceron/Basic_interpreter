from typing import List, Optional
from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter

class Basic:
    def __init__(self):
        self.interpreter = Interpreter()

    def run_line(self, line: str) -> None:
        lexer = Lexer(line)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        self.interpreter.interpret(ast)

    def run_program(self, program: str) -> None:
        # Split program into lines and run each line
        lines = program.split('\n')
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                self.run_line(line)

def main():
    basic = Basic()
    print("BASIC Interpreter v1.0")
    print("Type 'EXIT' to quit")
    
    while True:
        try:
            line = input(">>> ")
            if line.upper() == 'EXIT':
                break
            basic.run_line(line)
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()