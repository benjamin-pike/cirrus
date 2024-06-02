from lexer.tokens import TokenType  # Import the TokenType enumeration from lexer.tokens module

class Token:
    """
    The Token class represents a single token with its type, value, line number, and column number.

    Attributes:
        type (TokenType): The type of the token.
        value (str): The value or content of the token.
        line (int): The line number where the token is located in the source code.
        column (int): The column number where the token starts in the source code.
    """
    def __init__(self, type: TokenType, value: str, line: int, column: int) -> None:
        self.type: TokenType = type
        self.value: str = value
        self.line: int = line
        self.column: int = column

    def __repr__(self) -> str:
        return f'Token({self.type}, {self.value}, {self.line}, {self.column})'
