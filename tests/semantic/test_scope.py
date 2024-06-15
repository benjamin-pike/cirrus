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
                halt; // skip the current iteration
            }
            echo x;
        }
    """
    analyze_code(code)

def test_invalid_skip_statement():
    code = """
        if true {
            skip; // halt statement is only allowed in loop scopes
        }
    """

    with pytest.raises(SyntaxError, match=r'Skip statement is not valid outside of a loop block'):
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
