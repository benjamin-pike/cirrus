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

def test_undeclared_error():
    code = """
        int x = 5;
        echo y;  // 'y' is not declared
    """
    with pytest.raises(NameError, match=r'Variable "y" not declared'):
        analyze_code(code)

def test_scope_error():
    code = """
        int x = 5;
        {
            int y = x + 1;
        }
        echo y;  // 'y' is not declared in the outer scope
    """
    with pytest.raises(NameError, match=r'Variable "y" not declared'):
        analyze_code(code)

def test_type_error():
    code = """
        int x = "hello";  // Type mismatch
    """
    with pytest.raises(TypeError, match=r'Type mismatch for variable x: PrimitiveType\(TokenType.INT\) != PrimitiveType\(TokenType.STRING\)'):
        analyze_code(code)

def test_infer_primitive_type():
    code = """
        infer x = 5;
        echo x;
    """
    analyze_code(code)

def test_complex_infer_primitive_type():
    code = """
        infer x = 5;
        infer y = x + 5;
        echo y;
    """
    analyze_code(code)

def test_conflicting_infer_type():
    code = """
        infer x = 5;
        x = "hello";  // Conflicting types
    """
    with pytest.raises(TypeError, match=r'Type mismatch in assignment expression: PrimitiveType\(TokenType.INT\) != PrimitiveType\(TokenType.STRING\)'):
        analyze_code(code)

def test_conflicting_complex_infer_type():
    code = """
        infer x = 5;
        infer y = x + 5;
        y = "hello";  // Conflicting types
    """
    with pytest.raises(TypeError, match=r'Type mismatch in assignment expression: PrimitiveType\(TokenType.INT\) != PrimitiveType\(TokenType.STRING\)'):
        analyze_code(code)

def test_infer_array_type():
    code = """
        infer x = [1, 2, 3];

        each y in x {
            echo y + 1;
        }
    """
    analyze_code(code)

def test_conflicting_infer_array_type():
    code = """
        infer x = [1, 2, 3];
        x = "hello";  // Type mismatch
    """
    with pytest.raises(TypeError, match=r'Type mismatch in assignment expression: ArrayType\(PrimitiveType\(TokenType.INT\)\) != PrimitiveType\(TokenType.STRING\)'):
        analyze_code(code)

def test_function_declaration_and_call():
    code = """
        func multiply -> int = [int x, int y] >> {
            return x * y;
        }
        int result = multiply(4, 5);
    """
    analyze_code(code)

def test_function_variable_assignment_scope_error():
    code = """
        int x = 10;

        func add -> void = [int a, int b] >> {
            x = a + b;
        }
    """

    with pytest.raises(NameError, match=r'Variable "x" not declared in the function scope'):
        analyze_code(code)

def test_function_index_assignment_scope_error():
    code = """
        int[] arr = [1, 2, 3];

        func add -> void = [int[] a] >> {
            arr[0] = a;
        }
    """

    with pytest.raises(NameError, match=r'Variable "arr" not declared in the function scope'):
        analyze_code(code)

def test_nested_blocks_and_scopes():
    code = """
        int x = 5;
        {
            int y = x + 1;
            {
                int z = y + 2;
                echo z;
            }
            echo y;
        }
        echo x;
    """
    analyze_code(code)

def test_array_declaration_and_access():
    code = """
        int[] arr = [1, 2, 3];
        int x = arr[0];
    """
    analyze_code(code)

def test_mixed_array_declaration():
    code = """
        int[] arr = [1, 'hello', 3];  // Mixed types
    """

    with pytest.raises(TypeError, match=r'Inconsistent element types in array literal'):
        analyze_code(code)

def test_invalid_return_type():
    code = """
        func add -> int = [int a, int b] >> {
            return "hello";  // Type mismatch
        }
    """
    with pytest.raises(TypeError, match=r'Return type PrimitiveType\(TokenType.STRING\) does not match function return type PrimitiveType\(TokenType.INT\)'):
        analyze_code(code)

def test_invalid_return_usage():
    code = """
        if true {
            return 5; // Return statement should only be valid inside a function
        }
    """
    with pytest.raises(SyntaxError, match=r'Return statement is not valid outside of a function block'):
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

def test_invalid_function_call_type():
    code = """
        func add -> int = [int a, int b] >> {
            return a + b;
        }
        add(5, "hello");  // Type mismatch
    """
    with pytest.raises(TypeError, match=r'Argument type PrimitiveType\(TokenType.STRING\) does not match parameter type PrimitiveType\(TokenType.INT\)'):
        analyze_code(code)

def test_invalid_array_type():
    code = """
        int[] arr = [1, 2, 3];
        arr[0] = "hello";  // Type mismatch
    """
    with pytest.raises(TypeError, match=r'Type mismatch in assignment expression: PrimitiveType\(TokenType.INT\) != PrimitiveType\(TokenType.STRING\)'):
        analyze_code(code)

def test_array_index_error():
    code = """
        int[] arr = [1, 2, 3];
        int x = arr["string"];  // Index should be an integer
    """
    with pytest.raises(TypeError, match=r'Array index must be an integer'):
        analyze_code(code)

def test_if_else():
    code = """
        int x = 5;
        if x > 3 {
            echo "greater";
        } else {
            echo "smaller";
        }
    """
    analyze_code(code)

def test_while_loop():
    code = """
        int x = 0;
        while x < 10 {
            x++;
        }
    """
    analyze_code(code)

def test_each_statement():
    code = """
        each x in [1, 2, 3] {
            echo x;
        }
    """
    analyze_code(code)

def test_range_statement():
    code = """
        range x in 0 to 10 by 1 {
            echo x;
        }
    """
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
