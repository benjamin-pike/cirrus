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
    with pytest.raises(TypeError, match=r"Function `add` expects 2 arguments, got 1"):
        analyze_code(code)


def test_invalid_return_usage():
    code = """
        if (true) {
            return 5; // Return statement should only be valid inside a function
        }
    """
    with pytest.raises(
        SyntaxError, match=r"Return statement is not valid outside of a function block"
    ):
        analyze_code(code)


def test_complex_function():
    code = """
        int z = 15;
        func multiply -> int = [int x, int y] >> {
            return x * y;
        }
        if (z > 10) {
            z = multiply(z, 2);
        }
        while (z > 0) {
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
            each (x in arr) {
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
            each (x in arr) {
                result = fn(result, x);
            }
            return result;
        }

        int x = [[1, 2, 3, 4]] >> reduce(add) >> triple >> add;  // Type mismatch
    """
    with pytest.raises(TypeError, match=r"Function `add` expects 2 arguments, got 1"):
        analyze_code(code)


def test_function_parameter_types():
    code = """
        func add -> int = [int a, int b] >> {
            return a + b;
        }
        add(1, "2");  // Type mismatch in function parameters
    """
    with pytest.raises(
        TypeError,
        match=r"Argument type `PrimitiveType\(STR\)` does not match parameter type `PrimitiveType\(INT\)`",
    ):
        analyze_code(code)


def test_function_return_type():
    code = """
        func greet -> str = [str name] >> {
            return "Hello, " + name;
        }
        str message = greet("World");
    """
    analyze_code(code)


def test_infer_function_return_type():
    code = """
        func greet -> infer = [str name] >> {
            return "Hello, " + name;
        }
        
        int x = greet("World");  // Type mismatch
    """

    with pytest.raises(
        TypeError,
        match=r"Type mismatch for variable `x`: `PrimitiveType\(INT\)` != `PrimitiveType\(STR\)`",
    ):
        analyze_code(code)


def test_recursive_function():
    code = """
        func factorial -> int = [int n] >> {
            if (n <= 1) {
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
            each (x in arr) {
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


def test_function_literal():
    code = """
        func square -> int = [int x] >> {
            return x * x;
        }
        func apply -> int = [func<int, [int x]> fn, int y] >> {
            return fn(y);
        }
        int result = apply(func [int x] >> { return x * 2; }, 5);
    """
    analyze_code(code)


def test_template_declaration():
    code = """
        template Person = {
            str name;
            int age;
            
            func greet -> str = [] >> {
                return "Hello";
            }
        };
    """
    analyze_code(code)


def test_nested_template_declaration():
    code = """
        template User = {
            str name;
            int age;
            User[] followers;
        };
    """
    analyze_code(code)


def test_entity_declaration():
    code = """
        template Point = {
            int x;
            int y;
            
            func move -> void = [int dx, int dy] >> {
                x = x + dx;
                y = y + dy;
            }
        };
        
        entity pt = Point{x: 1, y: 2};
        
        pt.move(2, 3);
    """
    analyze_code(code)


def test_invalid_entity_declaration():
    code = """
        template Point = {
            int x;
            int y;
            
            func move -> void = [int dx, int dy] >> {
                x = x + dx;
                y = y + dy;
            }
        };
        
        entity point = Point{
            x: 1,
            z: 2,  // Invalid field
        };
    """
    with pytest.raises(
        NameError, match=r"Attribute `z` not defined in template `Point`"
    ):
        analyze_code(code)


def test_nested_entity_declaration():
    code = """
        template User = {
            str name;
            int age;
            User[] followers;
        };
        
        entity user = User{
            name: "James",
            age: 25,
            followers: [
                User{name: "Bob", age: 30, followers: []},
                User{name: "Charlie", age: 35, followers: []}
            ],
        };
    """
    analyze_code(code)


def test_invalid_nested_entity_declaration():
    code = """
        template User = {
            str name;
            int age;
            User[] followers;
        };
        
        entity user = User{
            name: "James",
            age: 25,
            followers: [
                User{name: "Bob", age: 30, followers: 2}, // Invalid `followers` type
                User{name: "Charlie", age: 35, followers: []}
            ],
        };
    """
    with pytest.raises(
        TypeError,
        match=r"Type mismatch for attribute `followers`: `ArrayType\(CustomType\(User\)\)` != `PrimitiveType\(INT\)`"
    ):
        analyze_code(code)


def test_set_method_call_expression():
    code = """
        int{} x = {1, 2, 3};
        bool y = x.add(4).remove(1).contains(2);
        int{} z = x.clear();
    """
    analyze_code(code)


def test_map_method_call_expression():
    code = """
        int{str} x = {"a": 1, "b": 2};
        int y = x.put("c", 3).remove("a").get("b");
        int{str} z = x.clear();
    """
    analyze_code(code)


def test_method_access_on_invalid_type():
    code = """
        int x = 5;
        x.add(4);  // Method call on non-object type
    """
    with pytest.raises(
        TypeError, match=r"Type `PrimitiveType\(INT\)` does not have methods"
    ):
        analyze_code(code)


def test_undeclared_method_access():
    code = """
        int{} x = {1, 2, 3};
        x.put(4);  // `put` is not a valid set method
    """
    with pytest.raises(
        TypeError,
        match=r"Method `put` is not defined on type `SetType\(PrimitiveType\(INT\)\)`",
    ):
        analyze_code(code)


def test_missing_method_arguments():
    code = """
        int{str} x = {"a": 1, "b": 2};
        x.put("c");  // Missing argument
    """
    with pytest.raises(TypeError, match=r"Method `put` expects 2 arguments, got 1"):
        analyze_code(code)


def test_invalid_method_argument_types():
    code = """
        int{str} x = {"a": 1, "b": 2};
        x.put(3, "c");  // Type mismatch in method arguments
    """

    with pytest.raises(
        TypeError,
        match=r"Argument type `PrimitiveType\(INT\)` does not match parameter type `PrimitiveType\(STR\)`",
    ):
        analyze_code(code)
