import argparse
from typing import Generator
from lexer.lexer import Lexer
from lexer.token import Token

def main(file_path: str) -> None:
    with open(file_path, 'r') as file:
        source_code = file.read()
    
    lexer: Lexer = Lexer(source_code)
    tokens: Generator[Token, None, None] = lexer.tokenize()
    
    for token in tokens:
        print(token)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a .crs script file.")
    parser.add_argument('file_path', type=str, help='The path to the .crs file')
    args = parser.parse_args()
    
    main(args.file_path)