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

def test_type_error():
    code = """
        int x = "hello";  // Type mismatch
    """
    with pytest.raises(TypeError, match=r'Type mismatch for variable x: PrimitiveType\(TokenType.INT\) != PrimitiveType\(TokenType.STRING\)'):
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

def test_conflicting_infer_array_type():
    code = """
        infer x = [1, 2, 3];
        x = "hello";  // Type mismatch
    """
    with pytest.raises(TypeError, match=r'Type mismatch in assignment expression: ArrayType\(PrimitiveType\(TokenType.INT\)\) != PrimitiveType\(TokenType.STRING\)'):
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

def test_infer_array_type():
    code = """
        infer x = [1, 2, 3];

        each y in x {
            echo y + 1;
        }
    """
    analyze_code(code)

def test_binary_expression_type_mismatch():
    code = """
        int x = 5 + "hello";  // Type mismatch in binary expression
    """
    with pytest.raises(TypeError, match=r'Type mismatch in binary expression: PrimitiveType\(TokenType.INT\) != PrimitiveType\(TokenType.STRING\)'):
        analyze_code(code)

def test_unary_expression_assignment_error():
    code = """
        func add -> int = [int a, int b] >> {
            return a + b;
        }

        int x = add(5, 10)++;
    """

    with pytest.raises(TypeError, match=r'Invalid assignment target for TokenType.INCREMENT'):
        analyze_code(code)

def test_logical_unary_expression_type_mismatch():
    code = """
        int x = 1;
        bool y = !x;  // Invalid operand type for unary NOT
    """
    with pytest.raises(TypeError, match=r'Invalid operand type for TokenType.LOGICAL_NOT: PrimitiveType\(TokenType.INT\)'):
        analyze_code(code)

def test_function_return_type_mismatch():
    code = """
        func foo -> int = [] >> {
            return "bar";  // Type mismatch in return statement
        }
    """
    with pytest.raises(TypeError, match=r'Return type PrimitiveType\(TokenType.STRING\) does not match function return type PrimitiveType\(TokenType.INT\)'):
        analyze_code(code)

def test_inconsistent_array_element_types():
    code = """
        int[] arr = [1, 2, "three"];  // Inconsistent element types
    """
    with pytest.raises(TypeError, match=r'Inconsistent element types in array literal'):
        analyze_code(code)

def test_array_index_type_mismatch():
    code = """
        int[] arr = [1, 2, 3];
        int x = arr[true];  // Array index must be an integer
    """
    with pytest.raises(TypeError, match=r'Array index must be an integer'):
        analyze_code(code)

def test_invalid_logical_operation():
    code = """
        int x = 2;
        int y = 5;
        bool z = x && y;  // Invalid operand type for logical AND
    """
    with pytest.raises(TypeError, match=r'Invalid operand type for TokenType.LOGICAL_AND: PrimitiveType\(TokenType.INT\)'):
        analyze_code(code)
