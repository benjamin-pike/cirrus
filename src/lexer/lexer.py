from typing import *
import re
from lexer.tokens import TokenType, spec
from lexer.token import Token

class Lexer:
    """
    The Lexer class is responsible for converting a string of source code into a stream of tokens
    that can be used by a parser. It uses regular expressions to identify token types based on
    predefined specifications.

    Attributes:
        code (str): The source code to be tokenised.
        line (int): The current line number being processed.
        column (int): The current column number being processed.
        pos (int): The current position in the source code string.
    """

    def __init__(self, code: str) -> None:
        """ Initialises the Lexer with the source code and sets the initial positions.

        Args:
            code (str): The source code to be tokenised.
        """
        self.code: str = code
        self.line: int = 1
        self.column: int = 1
        self.pos: int = 0

    def tokenize(self) -> Generator[Token, None, None]:
        """ Tokenises the source code into a sequence of tokens.

        Yields:
            Token: The next token in the source code.

        Raises:
            SyntaxError: If an invalid token is encountered.
        """
        # Compile the regular expression based on the token specification (spec = [(TokenType, regex), ...])
        regex: str = '|'.join(f'(?P<{pair[0].name}>{pair[1]})' for pair in spec)
        get_token = re.compile(regex).match  # Function to match regex from the current position
        mo: Optional[re.Match[str]] = get_token(self.code, self.pos)  # Initial match object

        while mo is not None:
            token_type: str | None = mo.lastgroup  # Type of the matched token

            if token_type is None:
                raise SyntaxError(f'Invalid token at line {self.line}')

            value: str = mo.group(token_type)  # Value of the matched token

            match TokenType[token_type]:
                case TokenType.DOUBLE_QUOTE | TokenType.SINGLE_QUOTE:
                    # Handle string literals separately
                    for token in self._match_string(token_type, value):
                        yield token
                    mo = get_token(self.code, self.pos)
                    continue
                case TokenType.NEWLINE:
                    self.line += 1
                    self.column = 1
                case TokenType.GAP:
                    self.column += len(value)  # Skip whitespace
                case TokenType.EOL_COMMENT:
                    self.line += 1
                    self.column = 1
                case TokenType.DELIMITED_COMMENT:
                    self.line += value.count('\n')
                    self.column = len(value.split('\n')[-1]) + 1
                case TokenType.MISMATCH:
                    raise SyntaxError(f'{value} unexpected on line {self.line}')
                case _:
                    yield Token(TokenType[token_type], value, self.line, self.column)
                    self.column += len(value)

            self.pos = mo.end()  # Update position to the end of the matched token
            mo = get_token(self.code, self.pos)  # Get the next match

        yield Token(TokenType.EOF, '', self.line, self.column)  # End of file token

    def _match_string(self, token_type: str, value: str) -> Generator[Token, None, None]:
        """ Handles the tokenization of string literals.

        Args:
            token_type (str): The type of the string token (single or double quote).
            value (str): The initial quote character.

        Yields:
            Token: Tokens representing parts of the string literal.

        Raises:
            SyntaxError: If an unterminated string literal is encountered.
        """
        quote_type = value

        yield Token(TokenType[token_type], value, self.line, self.column)  # Yield the opening quote

        self.pos += 1
        self.column += 1

        start_pos = self.pos
        start_line = self.line
        start_col = self.column
        while self.pos < len(self.code):
            if self.code[self.pos] == quote_type and self.code[self.pos - 1] != '\\':
                # Break if non-escaped closing quote is found
                break

            if self.code[self.pos] == '\n':
                # Support multi-line strings
                self.line += 1
                self.column = 1
            else:
                self.column += 1

            self.pos += 1

        if self.pos == len(self.code):
            raise SyntaxError(f"Unterminated string literal starting at line {start_line}")

        yield Token(TokenType.STRING_LITERAL, self.code[start_pos:self.pos], start_line, start_col)
        yield Token(TokenType[token_type], value, self.line, self.column)

        self.pos += 1
        self.column += 1
