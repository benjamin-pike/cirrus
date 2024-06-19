from typing import *
from frontend.lexer.token import Token
from frontend.lexer.tokens import TokenType
from frontend.syntax.ast import Program
from frontend.parser.typing import ParserABC
from frontend.parser.statements import StatementParser
from frontend.semantic.types import *


class Parser(ParserABC):
    """
    The Parser class is responsible for parsing a list
    of tokens into an abstract syntax tree (AST).

    Attributes:
        tokens (List[Token]): The list of tokens to be parsed.
        pos (int): The current position in the token list.
        statement_parser (StatementParser):
            An instance of StatementParser to handle statement parsing.
    """

    def __init__(self, tokens: List[Token]) -> None:
        """Initialises the Parser with a token list and creates a statement parser.

        Args:
            tokens (List[Token]): The list of tokens to be parsed.
        """
        self.tokens = tokens
        self.pos = 0  # Initialise the position in the token list
        self.statement_parser = StatementParser(self)  # Initialise the statement parser

    def parse(self) -> Program:
        """Parses the tokens into a Program AST node.

        Returns:
            Program: The root node of the parsed AST.
        """
        body = self.statement_parser.parse_statements()

        return Program(body)

    def consume(self, token_type: TokenType) -> Token:
        """Consumes the current token if it matches
        the expected type, otherwise raises an error.

        Args:
            token_type (TokenType): The expected type of the current token.

        Returns:
            Token: The consumed token.

        Raises:
            SyntaxError: If the current token type does not match the expected type.
        """
        token = self.current()
        if token.token_type != token_type:
            raise SyntaxError(
                f"Expected token {token_type}, but got {token.token_type}"
            )
        self.pos += 1

        return token

    def current(self) -> Token:
        """Retrieves the token at the current position.

        Returns:
            Token: The current token.

        Raises:
            RuntimeError: If the end of the token list is overrun.
        """
        if self.pos >= len(self.tokens):
            raise RuntimeError("End of file reached")

        return self.tokens[self.pos]

    def peek(self) -> Token:
        """Retrieves the token at the next position.

        Returns:
            Token: The next token.

        Raises:
            RuntimeError: If the end of the token list is overrun.
        """
        if self.pos + 1 >= len(self.tokens):
            raise RuntimeError("End of file reached")

        return self.tokens[self.pos + 1]

    def is_eof(self) -> bool:
        """Checks if the current token is the end-of-file token.

        Returns:
            bool: True if the current token is EOF, otherwise False.
        """
        return self.current().token_type == TokenType.EOF

    # Private methods
    def parse_var_type(self) -> VarType:
        """Parses a variable type.
        Delegates to _parse_function_type if the `func` keyword is encountered.

        Returns:
            VarType: The parsed variable type.
        """
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
                var_type = CustomType(self.consume(TokenType.IDENTIFIER).value)

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

    def parse_array_type(self, var_type: VarType) -> VarType:
        """Parses an array type.

        Args:
            var_type (VarType): The base type of the array.

        Returns:
            VarType: The parsed array type.
        """
        new_type = var_type

        while self.current().token_type == TokenType.LBRACKET:
            self.consume(TokenType.LBRACKET)
            self.consume(TokenType.RBRACKET)

            new_type = ArrayType(new_type)

        return new_type

    def parse_set_or_map_type(self, var_type: VarType) -> VarType:
        """Parses a set or map type.

        Args:
            var_type (VarType): The base type of the set or map.

        Returns:
            VarType: The parsed set or map type.
        """
        new_type = var_type

        while self.current().token_type == TokenType.LBRACE:
            self.consume(TokenType.LBRACE)
            if self.current().token_type == TokenType.RBRACE:
                self.consume(TokenType.RBRACE)

                new_type = SetType(var_type)
            else:
                key_type = self.parse_var_type()
                self.consume(TokenType.RBRACE)

                new_type = MapType(key_type, var_type)

        return new_type

    def parse_return_type(self) -> VarType:
        """Parses a return type for a function declaration.
        Extends the _parse_var_type method to handle the `void` keyword.

        Returns:
            VarType: The parsed return type.
        """
        if self.current().token_type == TokenType.VOID:
            self.consume(TokenType.VOID)
            return VoidType()

        return self.parse_var_type()

    def parse_function_type(self) -> FunctionType:
        """Parses a function type.

        Returns:
            FunctionType: The parsed function type.
        """
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
