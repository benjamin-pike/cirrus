from typing import *
import argparse
from lexer.lexer import Lexer
from lexer.token import Token
from parser.parser import Parser
from semantic.analyzer import SemanticAnalyzer

def main(file_path: str) -> None:
    with open(file_path, 'r') as file:
        source_code = file.read()

    lexer: Lexer = Lexer(source_code)
    tokens: List[Token] = list(lexer.tokenize())
    parser: Parser = Parser(list(tokens))

    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    print(ast)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a .crs script file.")
    parser.add_argument('file_path', type=str, help='The path to the .crs file')
    args = parser.parse_args()

    main(args.file_path)
