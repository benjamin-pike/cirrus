from typing import *
from lexer.token import Token  # Import the Token class
from lexer.tokens import TokenType  # Import the TokenType enumeration
from syntax.ast import Program  # Import the Program AST node
from parser._types import ParserABC  # Import the abstract base class for the parser
from parser.statements import StatementParser  # Import the StatementParser for parsing statements

class Parser(ParserABC):
    """
    The Parser class is responsible for parsing a list of tokens into an abstract syntax tree (AST).
    
    Attributes:
        tokens (List[Token]): The list of tokens to be parsed.
        pos (int): The current position in the token list.
        statement_parser (StatementParser): An instance of StatementParser to handle statement parsing.
    """
    def __init__(self, tokens: List[Token]) -> None:
        """
        Initialises the Parser with a list of tokens and sets up the statement parser.
        
        Args:
            tokens (List[Token]): The list of tokens to be parsed.
        """
        self.tokens = tokens
        self.pos = 0  # Initialise the position in the token list
        self.statement_parser = StatementParser(self)  # Initialise the statement parser with the current parser instance
         
    def parse(self) -> Program:
        """
        Parses the tokens into a Program AST node.
        
        Returns:
            Program: The root node of the parsed AST.
        """
        body = self.statement_parser.parse_statements()

        return Program(body)

    def consume(self, token_type: TokenType) -> Token:
        """
        Consumes the current token if it matches the expected type, otherwise raises an error.
        
        Args:
            token_type (TokenType): The expected type of the current token.
        
        Returns:
            Token: The consumed token.
        
        Raises:
            SyntaxError: If the current token type does not match the expected type.
        """
        token = self.current()
        if token.type != token_type:
            raise SyntaxError(f'Expected token {token_type}, but got {token.type}')
        self.pos += 1
        
        return token

    def current(self) -> Token:
        """
        Retrieves the token at the current position.
        
        Returns:
            Token: The current token.
        
        Raises:
            RuntimeError: If the end of the token list is overrun.
        """
        if self.pos >= len(self.tokens):
            raise RuntimeError('End of file reached')
        
        return self.tokens[self.pos]

    def is_eof(self) -> bool:
        """
        Checks if the current token is the end-of-file token.
        
        Returns:
            bool: True if the current token is EOF, otherwise False.
        """
        return self.current().type == TokenType.EOF