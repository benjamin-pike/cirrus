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


def test_undeclared_error():
    code = """
        int x = 5;
        echo y;  // 'y' is not declared
    """
    with pytest.raises(NameError, match=r'Variable "y" not declared'):
        analyze_code(code)


def test_redeclaration_error():
    code = """
        int x = 5;
        int x = 10;  // 'x' is already declared
    """
    with pytest.raises(NameError, match=r'Cannot redeclare variable "x"'):
        analyze_code(code)


def test_nested_redeclaration_error():
    code = """
        int x = 5;
        {
            int x = 10;  // 'x' is already declared
        }
    """
    with pytest.raises(NameError, match=r'Cannot shadow existing variable "x"'):
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


def test_function_variable_assignment_scope_error():
    code = """
        int x = 10;

        func add -> void = [int a, int b] >> {
            x = a + b;
        }
    """

    with pytest.raises(NameError, match=r'Variable "x" not declared'):
        analyze_code(code)


def test_non_local_function_variable_access():
    code = """
        int x = 10;

        func foo -> void = [] >> {
            echo x; // 'x' is not declared in the function scope
        }
    """

    with pytest.raises(NameError, match=r'Variable "x" not declared'):
        analyze_code(code)


def test_function_index_assignment_scope_error():
    code = """
        int[] arr = [1, 2, 3];

        func add -> void = [int[] a] >> {
            arr[0] = a;
        }
    """

    with pytest.raises(NameError, match=r'Variable "arr" not declared'):
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


def test_halt_statement():
    code = """
        int x = 0;
        while x < 10 {
            x++;
            if x == 5 {
                halt; // halt execution of the loop
            }
            echo x;
        }
    """
    analyze_code(code)


def test_invalid_skip_statement():
    code = """
        if true {
            skip; // skip statement is only allowed in loop scopes
        }
    """

    with pytest.raises(
        SyntaxError, match=r"Skip statement is not valid outside of a loop block"
    ):
        analyze_code(code)


def test_block_scope():
    code = """
        int x = 10;
        {
            int y = 20;
            echo y;
        }
        echo x;
        echo y; // y should not be accessible here
    """
    with pytest.raises(NameError, match=r'Variable "y" not declared'):
        analyze_code(code)


def test_nested_scopes():
    code = """
        int x = 5;
        {
            int y = 10;
            {
                int z = 15;
                echo z;
                echo y;
                echo x;
            }
            echo y;
            echo x;
        }
        echo x;
    """
    analyze_code(code)


def test_variable_lifetime():
    code = """
        int x = 5;
        {
            int y = x + 1;
            echo y; // y should be accessible here
        }
        echo y; // y should not be accessible here
    """
    with pytest.raises(NameError, match=r'Variable "y" not declared'):
        analyze_code(code)


def test_return_statement_reachability():
    code = """
        func foo -> void = [] >> {
            return;
            echo "This should be unreachable";  // Unreachable code
        }
    """
    with pytest.raises(SyntaxError, match=r"Unreachable code detected"):
        analyze_code(code)


def test_halt_statement_reachability():
    code = """
        while true {
            halt;
            echo "This should be unreachable";  // Unreachable code
        }
    """
    with pytest.raises(SyntaxError, match=r"Unreachable code detected"):
        analyze_code(code)


def test_skip_statement_reachability():
    code = """
        while true {
            skip;
            echo "This should be unreachable";  // Unreachable code
        }
    """
    with pytest.raises(SyntaxError, match=r"Unreachable code detected"):
        analyze_code(code)


def test_valid_control_flow_statement_use():
    code = """
        func main -> int = [] >> {
            int x = 0;

            while x < 10 {
                x++;
                if x == 5 { skip; }
                if x == 7 { halt; }
                echo x;
            }

            return x;
        }

        main();
    """
    analyze_code(code)


def test_nested_if_else_reachability():
    code = """
        func foo -> void = [] >> {
            int x = 5;

            if x > 3 {
                if x < 10 {
                    return;
                } else {
                    return;
                }
            } else {
                return;
            }

            echo "This should be unreachable";  // Unreachable code
        }
    """
    with pytest.raises(SyntaxError, match=r"Unreachable code detected"):
        analyze_code(code)


def test_unreachable_if_block():
    code = """
        func foo -> void = [] >> {
            if false {
                echo "This should be unreachable";  // Unreachable code
            } else {
                return;
            }
        }
    """
    with pytest.raises(SyntaxError, match=r"Unreachable if block detected"):
        analyze_code(code)


def test_unreachable_else_block():
    code = """
        func foo -> void = [] >> {
            if true {
                return;
            } else {
                echo "This should be unreachable";  // Unreachable code
            }
        }
    """
    with pytest.raises(SyntaxError, match=r"Unreachable else block detected"):
        analyze_code(code)
