from lexer.lexer import Lexer
from parser.parser import Parser

def repl():
    print("Cirrus REPL v0.1.0")
    
    while True:
        try:
            src = input("cirrus >> ")
            
            if src.strip() == "" or src == "exit":
                print("Exiting REPL")
                break

            tokens = list(Lexer(src).tokenize())
            parser = Parser(tokens)
            ast = parser.parse()
            
            print(ast)
        except (EOFError):
            print("\nExiting REPL")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    repl()