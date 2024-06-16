from typing import List
import argparse
from frontend.lexer.lexer import Lexer
from frontend.lexer.token import Token
from frontend.parser.parser import Parser
from frontend.semantic.analyzer import SemanticAnalyzer


def main(file_path: str) -> None:
    """Main function to process a .crs script file."""

    with open(file_path, "r", encoding="UTF-8") as file:
        source_code = file.read()

    lexer: Lexer = Lexer(source_code)
    tokens: List[Token] = list(lexer.tokenize())
    parser: Parser = Parser(list(tokens))

    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    print(ast)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Process a .crs script file.")
    arg_parser.add_argument("file_path", type=str, help="The path to the .crs file")
    args = arg_parser.parse_args()

    main(args.file_path)
