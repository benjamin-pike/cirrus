import re
import pytest
from frontend.lexer.lexer import Lexer
from frontend.parser.parser import Parser
from frontend.syntax.ast import *


def parse_code(code: str) -> Program:
    lexer = Lexer(code)
    tokens = list(lexer.tokenize())
    parser = Parser(tokens)
    return parser.parse()


def check(code: str, error: str):
    with pytest.raises(SyntaxError, match=re.escape(error)):
        parse_code(code)


def test_missing_semicolon():
    code = "int x = 5"
    check(code, "Expected token TokenType.SEMICOLON, but got TokenType.EOF")


def test_invalid_unterminated_string_literal():
    code = "echo 'hello world;"
    check(code, "Unterminated string literal starting at line 1")


def test_unmatched_bracket():
    code = "int x = [1, 2, 3;"
    check(code, "Expected token TokenType.RBRACKET, but got TokenType.SEMICOLON")


def test_unmatched_brace():
    code = "{ int y = 20; y - 5;"
    check(code, "Expected token TokenType.RBRACE, but got TokenType.EOF")


def test_unmatched_parenthesis():
    code = "if (x > 5 { return x; }"
    check(code, "Expected token TokenType.RPAREN, but got TokenType.LBRACE")


def test_invalid_token():
    code = "let x = 5 @ 3;"
    check(code, "@ unexpected on line 1")


def test_extra_closing_bracket():
    code = "int[] x = [1, 2, 3]];"
    check(code, "Expected token TokenType.SEMICOLON, but got TokenType.RBRACKET")


def test_extra_closing_brace():
    code = "{ int y = 20; y - 5; }}"
    check(code, "Unexpected token Token(TokenType.RBRACE, }, 1, 23)")


def test_extra_closing_parenthesis():
    code = "if (x > 5)) { return x; }"
    check(code, "Expected token TokenType.LBRACE, but got TokenType.RPAREN")


def test_double_operators():
    code = "int x = 5 ++ 3;"
    check(code, "Expected token TokenType.SEMICOLON, but got TokenType.INT_LITERAL")


def test_incomplete_expression():
    code = "int x = ;"
    check(code, "Unexpected token Token(TokenType.SEMICOLON, ;, 1, 9)")


def test_missing_operator():
    code = "int x = 5 5;"
    check(code, "Expected token TokenType.SEMICOLON, but got TokenType.INT_LITERAL")


def test_unexpected_keyword():
    code = "int if = 5;"
    check(code, "Expected token TokenType.IDENTIFIER, but got TokenType.IF")


def test_invalid_function_declaration():
    code = "func add = a, b >> { return a + b; }"
    check(code, "Expected token TokenType.RETURN_ARROW, but got TokenType.ASSIGN")


def test_missing_function_body():
    code = "func add -> int = [int a, int b] >> ;"
    check(code, "Expected token TokenType.LBRACE, but got TokenType.SEMICOLON")


def test_invalid_array_literal():
    code = "int arr = [1, 2, ];"
    check(code, "Unexpected token Token(TokenType.RBRACKET, ], 1, 18)")


def test_invalid_set_literal():
    code = "int{} x = {'a', 'b', 'c': 3 };"
    check(code, "Expected token TokenType.RBRACE, but got TokenType.COLON")
    

def test_invalid_map_literal():
    code = "int{str} x = {'a': 1, 'b', 'c': 3};"
    check(code, "Expected token TokenType.COLON, but got TokenType.COMMA")


def test_invalid_pipe_expression():
    code = "[[1, 2, 3]] >> map(triple) >> ;"
    check(code, "Expected token TokenType.IDENTIFIER, but got TokenType.SEMICOLON")


def test_invalid_return_statement():
    code = "return"
    check(code, "Unexpected token Token(TokenType.EOF, , 1, 7)")


def test_incomplete_block_statement():
    code = "{ int y = 20; y - ; }"
    check(code, "Unexpected token Token(TokenType.SEMICOLON, ;, 1, 19)")


def test_invalid_assignment():
    code = "int x == 10;"
    check(code, "Expected token TokenType.ASSIGN, but got TokenType.EQUAL")


def test_double_variable_declaration():
    code = "int int x = 10;"
    check(code, "Expected token TokenType.IDENTIFIER, but got TokenType.INT")


def test_extra_comma_in_function_call():
    code = "foo(a, b, );"
    check(code, "Unexpected token Token(TokenType.RPAREN, ), 1, 11)")


def test_invalid_range_statement():
    code = "range (x in 0 to 10 step 2) { return x; }"
    check(code, "Expected token TokenType.RPAREN, but got TokenType.IDENTIFIER")
