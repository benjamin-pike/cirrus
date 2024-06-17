import pytest
from frontend.lexer.lexer import Lexer
from frontend.parser.parser import Parser
from frontend.semantic.analyzer import SemanticAnalyzer
from frontend.syntax.ast import *


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
    with pytest.raises(
        TypeError,
        match=r"Type mismatch for variable `x`: `PrimitiveType\(INT\)` != `PrimitiveType\(STRING\)`",
    ):
        analyze_code(code)


def test_conflicting_infer_type():
    code = """
        infer x = 5;
        x = "hello";  // Conflicting types
    """
    with pytest.raises(
        TypeError,
        match=r"Type mismatch in assignment expression: PrimitiveType\(INT\) != PrimitiveType\(STRING\)",
    ):
        analyze_code(code)


def test_conflicting_complex_infer_type():
    code = """
        infer x = 5;
        infer y = x + 5;
        y = "hello";  // Conflicting types
    """
    with pytest.raises(
        TypeError,
        match=r"Type mismatch in assignment expression: PrimitiveType\(INT\) != PrimitiveType\(STRING\)",
    ):
        analyze_code(code)


def test_conflicting_infer_array_type():
    code = """
        infer x = [1, 2, 3];
        x = "hello";  // Type mismatch
    """
    with pytest.raises(
        TypeError,
        match=r"Type mismatch in assignment expression: ArrayType\(PrimitiveType\(INT\)\) != PrimitiveType\(STRING\)",
    ):
        analyze_code(code)


def test_mixed_array_declaration():
    code = """
        int[] arr = [1, 'hello', 3];  // Mixed types
    """
    with pytest.raises(TypeError, match=r"Invalid element type in array literal"):
        analyze_code(code)


def test_invalid_return_type():
    code = """
        func add -> int = [int a, int b] >> {
            return "hello";  // Type mismatch
        }
    """
    with pytest.raises(
        TypeError,
        match=r"Return type `PrimitiveType\(STRING\)` does not match function return type `PrimitiveType\(INT\)`",
    ):
        analyze_code(code)


def test_invalid_function_call_type():
    code = """
        func add -> int = [int a, int b] >> {
            return a + b;
        }
        add(5, "hello");  // Type mismatch
    """
    with pytest.raises(
        TypeError,
        match=r"Argument type `PrimitiveType\(STRING\)` does not match parameter type `PrimitiveType\(INT\)`",
    ):
        analyze_code(code)


def test_invalid_array_type():
    code = """
        int[] arr = [1, 2, 3];
        arr[0] = "hello";  // Type mismatch
    """
    with pytest.raises(
        TypeError,
        match=r"Type mismatch in assignment expression: PrimitiveType\(INT\) != PrimitiveType\(STRING\)",
    ):
        analyze_code(code)


def test_invalid_set_type():
    code = """
        int{} set = {1, 'hello', 3};
    """

    with pytest.raises(TypeError, match=r"Invalid element type in set literal"):
        analyze_code(code)


def test_invalid_map_key_type():
    code = """
        int{string} map = {1: 1, 'world': 2};
    """

    with pytest.raises(TypeError, match=r"Invalid key type in map literal"):
        analyze_code(code)


def test_invalid_map_value_type():
    code = """
        int{string} map = {'hello': 1, 'world': 'invalid'};
    """

    with pytest.raises(TypeError, match=r"Invalid value type in map literal"):
        analyze_code(code)


def test_unhashable_set_element_type():
    code = """
        int[]{} set = {[1, 2, 3], [4, 5, 6]};
    """

    with pytest.raises(TypeError, match=r"Element type of set must be hashable"):
        analyze_code(code)


def test_unhashable_map_key_type():
    code = """
        int{int[]} map = {[1, 2, 3]: 1, [4, 5, 6]: 2};
    """

    with pytest.raises(TypeError, match=r"Key type of map must be hashable"):
        analyze_code(code)


def test_array_index_error():
    code = """
        int[] arr = [1, 2, 3];
        int x = arr["string"];  // Index should be an integer
    """
    with pytest.raises(TypeError, match=r"Array index must be an integer"):
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
    with pytest.raises(
        TypeError,
        match=r"Type mismatch in binary expression: PrimitiveType\(INT\) != PrimitiveType\(STRING\)",
    ):
        analyze_code(code)


def test_unary_expression_assignment_error():
    code = """
        func add -> int = [int a, int b] >> {
            return a + b;
        }

        int x = add(5, 10)++;
    """

    with pytest.raises(
        TypeError, match=r"Invalid assignment target for TokenType.INCREMENT"
    ):
        analyze_code(code)


def test_logical_unary_expression_type_mismatch():
    code = """
        int x = 1;
        bool y = !x;  // Invalid operand type for unary NOT
    """
    with pytest.raises(
        TypeError,
        match=r"Invalid operand type for TokenType.LOGICAL_NOT: PrimitiveType\(INT\)",
    ):
        analyze_code(code)


def test_function_return_type_mismatch():
    code = """
        func foo -> int = [] >> {
            return "bar";  // Type mismatch in return statement
        }
    """
    with pytest.raises(
        TypeError,
        match=r"Return type `PrimitiveType\(STRING\)` does not match function return type `PrimitiveType\(INT\)`",
    ):
        analyze_code(code)


def test_invalid_array_element_type():
    code = """
        int[] arr = [1, 2, "three"];  // Invalid element type
    """
    with pytest.raises(TypeError, match=r"Invalid element type in array literal"):
        analyze_code(code)


def test_array_index_type_mismatch():
    code = """
        int[] arr = [1, 2, 3];
        int x = arr[true];  // Array index must be an integer
    """
    with pytest.raises(TypeError, match=r"Array index must be an integer"):
        analyze_code(code)


def test_invalid_logical_operation():
    code = """
        int x = 2;
        int y = 5;
        bool z = x && y;  // Invalid operand type for logical AND
    """
    with pytest.raises(
        TypeError,
        match=r"Invalid operand type for TokenType.LOGICAL_AND: PrimitiveType\(INT\)",
    ):
        analyze_code(code)
