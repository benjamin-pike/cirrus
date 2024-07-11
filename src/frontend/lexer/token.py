from frontend.lexer.tokens import TokenType


class Token:
    """Represents a token with its type, value, line number, and column number."""

    def __init__(
        self, token_type: TokenType, value: str, line: int, column: int
    ) -> None:
        self.token_type: TokenType = token_type
        self.value: str = value
        self.line: int = line
        self.column: int = column

    def __repr__(self) -> str:
        return f"Token({self.token_type}, {self.value}, {self.line}, {self.column})"
