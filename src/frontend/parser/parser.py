from typing import *
from frontend.lexer.token import Token
from frontend.lexer.tokens import TokenType
from frontend.syntax.ast import Program
from frontend.parser.typing import ParserABC
from frontend.parser.statements import StatementParser


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

    def is_eof(self) -> bool:
        """Checks if the current token is the end-of-file token.

        Returns:
            bool: True if the current token is EOF, otherwise False.
        """
        return self.current().token_type == TokenType.EOF
