import pytest

from lexer.lexer import Lexer
from parser.parser import Parser
from syntax.ast import *

def parse_code(code: str) -> Program:
    lexer = Lexer(code)
    tokens = list(lexer.tokenize())
    parser = Parser(tokens)
    return parser.parse()

def check(code: str):
    with pytest.raises(SyntaxError):
        parse_code(code)

def test_missing_semicolon():
    code = "let x = 5"
    check(code)

def test_invalid_unterminated_string_literal():
    code = "echo 'hello world;"
    check(code)

def test_unmatched_bracket():
    code = "let x = [1, 2, 3;"
    check(code)

def test_unmatched_brace():
    code = "{ let y = 20; y - 5;"
    check(code)

def test_unmatched_parenthesis():
    code = "if (x > 5 { return x; }"
    check(code)

def test_invalid_token():
    code = "let x = 5 @ 3;"
    check(code)

def test_extra_closing_bracket():
    code = "let x = [1, 2, 3]];"
    check(code)

def test_extra_closing_brace():
    code = "{ let y = 20; y - 5; }}"
    check(code)

def test_extra_closing_parenthesis():
    code = "if (x > 5)) { return x; }"
    check(code)

def test_double_operators():
    code = "let x = 5 ++ 3;"
    check(code)

def test_incomplete_expression():
    code = "let x = ;"
    check(code)

def test_missing_operator():
    code = "let x = 5 5;"
    check(code)

def test_unexpected_keyword():
    code = "let if = 5;"
    check(code)

def test_invalid_function_declaration():
    code = "func add = a, b >> { return a + b; }"
    check(code)

def test_missing_function_body():
    code = "func add = [a, b] >> ;"
    check(code)

def test_invalid_array_literal():
    code = "let arr = [1, 2, ];"
    check(code)

def test_invalid_pipe_expression():
    code = "[[1, 2, 3]] >> map(triple) >> ;"
    check(code)

def test_invalid_return_statement():
    code = "return;"
    check(code)

def test_incomplete_block_statement():
    code = "{ let y = 20; y - ; }"
    check(code)

def test_invalid_assignment():
    code = "int x == 10;"
    check(code)

def test_double_variable_declaration():
    code = "let let x = 10;"
    check(code)

def test_extra_comma_in_function_call():
    code = "func(a, b, );"
    check(code)

def test_invalid_range_statement():
    code = "range x in 0 to 10 step 2 { return x; }"
    check(code)
