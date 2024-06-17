from typing import List, Protocol
from abc import ABC, abstractmethod
from frontend.lexer.token import Token
from frontend.lexer.tokens import TokenType
from frontend.syntax.ast import *


class ExpressionParserABC(Protocol):
    """Abstract base class for the expression parser."""

    @abstractmethod
    def parse_expression(self) -> Expression:
        """Parses a general expression."""

    @abstractmethod
    def parse_assignment_expression(self) -> Expression:
        """Parses an assignment expression."""

    @abstractmethod
    def parse_binary_expression(self, precedence: int) -> Expression:
        """Parses a binary expression."""

    @abstractmethod
    def parse_unary_expression(self) -> Expression:
        """Parses a unary expression."""

    @abstractmethod
    def parse_primary_expression(self) -> Expression:
        """Parses a primary expression."""

    @abstractmethod
    def parse_identifier_expression(self) -> Expression:
        """Parses an identifier expression."""

    @abstractmethod
    def parse_function_call_expression(
        self, callee: Identifier
    ) -> FunctionCallExpression:
        """Parses a function call expression."""

    @abstractmethod
    def parse_arguments(self) -> List[Expression]:
        """Parses a list of arguments."""

    @abstractmethod
    def parse_array_literal(self) -> Expression:
        """Parses an array literal."""

    @abstractmethod
    def parse_set_literal(self) -> Expression:
        """Parses a set literal."""

    @abstractmethod
    def parse_map_literal(self, first_key: Expression) -> Expression:
        """Parses a map literal."""

    @abstractmethod
    def parse_index_expression(self, array: Expression) -> IndexExpression:
        """Parses an index expression."""

    @abstractmethod
    def parse_member_access_expression(self, obj: Expression) -> Expression:
        """Parses a member access expression."""

    @abstractmethod
    def parse_method_call_expression(
        self, obj: Expression, method: Identifier
    ) -> MethodCallExpression:
        """Parses a method call expression."""

    @abstractmethod
    def parse_pipe_expression(self, args: List[Expression]) -> Expression:
        """Parses a pipe expression."""


class StatementParserABC(Protocol):
    """Abstract base class for the statement parser."""

    expression_parser: ExpressionParserABC

    @abstractmethod
    def parse_statements(self) -> List[Statement]:
        """Iteratively parses statements until the end of the program."""

    @abstractmethod
    def parse_statement(self) -> Statement:
        """Parses a single statement based on the current token type."""

    @abstractmethod
    def parse_expression_statement(self) -> ExpressionStatement:
        """Parses an expression statement."""

    @abstractmethod
    def parse_variable_declaration(self) -> VariableDeclaration:
        """Parses a variable declaration statement."""

    @abstractmethod
    def parse_block_statement(self) -> BlockStatement:
        """Parses a block statement."""

    @abstractmethod
    def parse_if_statement(self) -> IfStatement:
        """Parses an if statement."""

    @abstractmethod
    def parse_while_statement(self) -> WhileStatement:
        """Parses a while statement."""

    @abstractmethod
    def parse_range_statement(self) -> RangeStatement:
        """Parses a range statement."""

    @abstractmethod
    def parse_each_statement(self) -> EachStatement:
        """Parses an each statement."""

    @abstractmethod
    def parse_halt_statement(self) -> HaltStatement:
        """Parses a halt statement."""

    @abstractmethod
    def parse_skip_statement(self) -> SkipStatement:
        """Parses a skip statement."""

    @abstractmethod
    def parse_return_statement(self) -> ReturnStatement:
        """Parses a return statement."""

    @abstractmethod
    def parse_function_declaration(self) -> FunctionDeclaration:
        """Parses a function declaration statement."""

    @abstractmethod
    def parse_echo_statement(self) -> EchoStatement:
        """Parses an echo statement."""


class ParserABC(ABC):
    """Abstract base class for the main program parser."""

    statement_parser: StatementParserABC

    @abstractmethod
    def parse(self) -> Program:
        """Parses the tokens into a Program AST node."""

    @abstractmethod
    def consume(self, token_type: TokenType) -> Token:
        """Consumes the current token if it matches the
        expected type, otherwise raises an error."""

    @abstractmethod
    def current(self) -> Token:
        """Retrieves the token at the current position."""

    @abstractmethod
    def is_eof(self) -> bool:
        """Checks if the current token is the end-of-file token."""
