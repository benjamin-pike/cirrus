from typing import *
from frontend.lexer.token import Token
from frontend.lexer.tokens import TokenType
from frontend.syntax.ast import Program
from frontend.parser.typing import ParserABC
from frontend.parser.statements import StatementParser
from frontend.semantic.types import *


class Parser(ParserABC):
    """Parses an AST from a list of tokens."""

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0
        self.statement_parser = StatementParser(self)

    def parse(self) -> Program:
        body = self.statement_parser.parse_statements()

        return Program(body)

    def consume(self, token_type: TokenType) -> Token:
        token = self.current()
        if token.token_type != token_type:
            raise SyntaxError(
                f"Expected token {token_type}, but got {token.token_type}"
            )
        self.pos += 1

        return token

    def current(self) -> Token:
        if self.pos >= len(self.tokens):
            raise RuntimeError("End of file reached")

        return self.tokens[self.pos]

    def is_eof(self) -> bool:
        return self.current().token_type == TokenType.EOF

    def parse_var_type(self) -> VarType:
        if self.current().token_type == TokenType.FUNC:
            return self.parse_function_type()

        match self.current().token_type:
            case TokenType.INT:
                var_type = PrimitiveType(self.consume(TokenType.INT).token_type)
            case TokenType.FLOAT:
                var_type = PrimitiveType(self.consume(TokenType.FLOAT).token_type)
            case TokenType.STR:
                var_type = PrimitiveType(self.consume(TokenType.STR).token_type)
            case TokenType.BOOL:
                var_type = PrimitiveType(self.consume(TokenType.BOOL).token_type)
            case TokenType.INFER:
                var_type = InferType()
                self.consume(TokenType.INFER)
            case TokenType.IDENTIFIER:
                var_type = CustomTypeIdentifier(
                    self.consume(TokenType.IDENTIFIER).value
                )

            case _:
                raise SyntaxError(f"Unexpected token {self.current()}")

        while self.current().token_type in (
            TokenType.LBRACKET,
            TokenType.LBRACE,
        ):
            if self.current().token_type == TokenType.LBRACKET:
                var_type = self.parse_array_type(var_type)
            if self.current().token_type == TokenType.LBRACE:
                var_type = self.parse_set_or_map_type(var_type)

        return var_type

    def parse_array_type(self, element_type: VarType) -> VarType:
        new_type = element_type

        while self.current().token_type == TokenType.LBRACKET:
            self.consume(TokenType.LBRACKET)
            self.consume(TokenType.RBRACKET)

            new_type = ArrayType(new_type)

        return new_type

    def parse_set_or_map_type(self, element_type: VarType) -> VarType:
        new_type = element_type

        while self.current().token_type == TokenType.LBRACE:
            self.consume(TokenType.LBRACE)
            if self.current().token_type == TokenType.RBRACE:
                self.consume(TokenType.RBRACE)

                new_type = SetType(element_type)
            else:
                key_type = self.parse_var_type()
                self.consume(TokenType.RBRACE)

                new_type = MapType(key_type, element_type)

        return new_type

    def parse_return_type(self) -> VarType:
        if self.current().token_type == TokenType.VOID:
            self.consume(TokenType.VOID)
            return VoidType()

        return self.parse_var_type()

    def parse_function_type(self) -> FunctionType:
        self.consume(TokenType.FUNC)
        self.consume(TokenType.LT)

        return_type = self.parse_return_type()

        self.consume(TokenType.COMMA)
        self.consume(TokenType.LBRACKET)

        parameters: List[Tuple[str, VarType]] = []
        while self.current().token_type != TokenType.RBRACKET:
            var_type = self.parse_var_type()
            identifier = self.consume(TokenType.IDENTIFIER).value
            parameters.append((identifier, var_type))

            if self.current().token_type == TokenType.COMMA:
                self.consume(TokenType.COMMA)

        self.consume(TokenType.RBRACKET)
        self.consume(TokenType.GT)

        return FunctionType(return_type, parameters)
