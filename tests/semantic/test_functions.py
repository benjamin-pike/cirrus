import pytest
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.analyzer import SemanticAnalyzer
from syntax.ast import *

def parse_code(code: str) -> Program:
    lexer = Lexer(code)
    tokens = list(lexer.tokenize())
    parser = Parser(tokens)
    return parser.parse()

def analyze_code(code: str):
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

def test_valid_program():
    code = """
        int x = 5;
        func add -> int = [int a, int b] >> {
            return a + b;
        }
        echo add(2, 3);
    """
    analyze_code(code)

def test_function_declaration_and_call():
    code = """
        func multiply -> int = [int x, int y] >> {
            return x * y;
        }
        int result = multiply(4, 5);
    """
    analyze_code(code)

def test_function_redeclaration_error():
    code = """
        func add -> int = [int a, int b] >> {
            return a + b;
        }
        func add -> int = [int a, int b] >> {  // 'add' is already declared
            return a + b;
        }
    """
    with pytest.raises(NameError, match=r'Cannot redeclare function "add"'):
        analyze_code(code)

def test_invalid_function_call():
    code = """
        func add -> int = [int a, int b] >> {
            return a + b;
        }
        add(5);  // Missing argument
    """
    with pytest.raises(TypeError, match=r'Function add expects 2 arguments, got 1'):
        analyze_code(code)

def test_invalid_return_usage():
    code = """
        if true {
            return 5; // Return statement should only be valid inside a function
        }
    """
    with pytest.raises(SyntaxError, match=r'Return statement is not valid outside of a function block'):
        analyze_code(code)

def test_complex_function():
    code = """
        int z = 15;
        func multiply -> int = [int x, int y] >> {
            return x * y;
        }
        if z > 10 {
            z = multiply(z, 2);
        }
        while z > 0 {
            z = z - 1;
        }
    """
    analyze_code(code)

def test_pipe_expression():
    code = """
        func add -> int = [int a, int b] >> {
            return a + b;
        }

        func triple -> int = [int x] >> {
            return x * 3;
        }

        func reduce -> int = [int[] arr, func<int, [int a, int b]> fn] >> {
            int result = 0;
            each x in arr {
                result = fn(result, x);
            }
            return result;
        }

        int x = [[1, 2, 3, 4]] >> reduce(add) >> triple;
    """
    analyze_code(code)
    code = """
        func add -> int = [int a, int b] >> {
            return a + b;
        }

        func triple -> int = [int x] >> {
            return x * 3;
        }

        func reduce -> int = [int[] arr, func<int, [int a, int b]> fn] >> {
            int result = 0;
            each x in arr {
                result = fn(result, x);
            }
            return result;
        }

        int x = [[1, 2, 3, 4]] >> reduce(add) >> triple >> add;  // Type mismatch
    """
    with pytest.raises(TypeError, match=r'Function add expects 2 arguments, got 1'):
        analyze_code(code)

def test_function_parameter_types():
    code = """
        func add -> int = [int a, int b] >> {
            return a + b;
        }
        add(1, "2");  // Type mismatch in function parameters
    """
    with pytest.raises(TypeError, match=r'Argument type PrimitiveType\(TokenType.STRING\) does not match parameter type PrimitiveType\(TokenType.INT\)'):
        analyze_code(code)

def test_function_return_type():
    code = """
        func greet -> string = [string name] >> {
            return "Hello, " + name;
        }
        string message = greet("World");
    """
    analyze_code(code)

def test_recursive_function():
    code = """
        func factorial -> int = [int n] >> {
            if n <= 1 {
                return 1;
            } else {
                return n * factorial(n - 1);
            }
        }
        int result = factorial(5);
    """
    analyze_code(code)

def test_function_with_array_parameter():
    code = """
        func sum -> int = [int[] arr] >> {
            int result = 0;
            each x in arr {
                result = result + x;
            }
            return result;
        }
        int[] numbers = [1, 2, 3, 4, 5];
        int total = sum(numbers);
    """
    analyze_code(code)

def test_function_with_nested_call():
    code = """
        func multiply -> int = [int x, int y] >> {
            return x * y;
        }
        func square -> int = [int x] >> {
            return multiply(x, x);
        }
        int result = square(4);
    """
    analyze_code(code)
