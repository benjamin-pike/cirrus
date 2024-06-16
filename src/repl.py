from frontend.lexer.lexer import Lexer
from frontend.parser.parser import Parser
from frontend.semantic.analyzer import SemanticAnalyzer


def repl():
    """Read-Eval-Print Loop"""

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
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)

            print(ast)
        except EOFError:
            print("\nExiting REPL")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    repl()
