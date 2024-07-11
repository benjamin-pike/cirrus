from typing import List, Protocol
from abc import ABC, abstractmethod
from frontend.lexer.token import Token
from frontend.lexer.tokens import TokenType
from frontend.syntax.ast import *


class ExpressionParserABC(Protocol):
    """Abstract base class for expression parsers."""

    @abstractmethod
    def parse_expression(self) -> Expression:
        """Parses a general expression.

        Returns:
            Expression: The parsed expression.
        """

    @abstractmethod
    def parse_assignment_expression(self) -> Expression:
        """Parses an assignment expression.

        Returns:
            Expression: The parsed assignment expression or the result of
            `parse_binary_expression`.

        Raises:
            SyntaxError: If the left-hand side of the assignment is not a valid
            identifier or index expression.
        """

    @abstractmethod
    def parse_binary_expression(self, precedence: int) -> Expression:
        """Parses a binary expression according to operator precedence.

        Args:
            precedence (int): The current precedence level.

        Returns:
            Expression: The parsed binary expression or the result of
            `parse_unary_expression`.
        """

    @abstractmethod
    def parse_unary_expression(self) -> Expression:
        """Parses a unary expression, handling prefix and postfix operators.

        Returns:
            Expression: The parsed unary expression or the result of
            `parse_primary_expression`.
        """

    @abstractmethod
    def parse_primary_expression(self) -> Expression:
        """Parses a primary expression, which can be literals or identifiers.

        Returns:
            Expression: The parsed primary expression or the result of
            `parse_expression`.

        Raises:
            SyntaxError: If the current token is not a valid primary expression.
        """

    @abstractmethod
    def parse_identifier_expression(self) -> Expression:
        """Parses an identifier expression.

        Returns:
            Expression: The parsed identifier or the result of
            `parse_method_call_expression` or `parse_method_call_expression`
        """

    @abstractmethod
    def parse_function_literal(self) -> FunctionLiteral:
        """Parses a function literal expression.

        Returns:
            FunctionLiteral: The parsed function literal expression.
        """

    @abstractmethod
    def parse_function_call_expression(
        self, callee: Identifier
    ) -> FunctionCallExpression:
        """Parses a function function call expression.

        Args:
            callee (Expression): The function being called.

        Returns:
            FunctionCallExpression: The parsed function call expression.
        """

    @abstractmethod
    def parse_arguments(self) -> List[Expression]:
        """Parses the arguments of a function call.

        Returns:
            List[Expression]: The list of parsed argument expressions.
        """

    @abstractmethod
    def parse_array_literal(self) -> Expression:
        """Parses an array literal.

        Returns:
            Expression: The parsed array literal or the result of
            `parse_pipe_expression.`
        """

    @abstractmethod
    def parse_set_literal(self) -> Expression:
        """Parses a set literal.

        Returns:
            Expression: The parsed set literal or the result of `parse_map_literal`.
        """

    @abstractmethod
    def parse_map_literal(self, first_key: Expression) -> Expression:
        """Parses an map literal

        Args:
            first_key (Expression): The first key in the map literal.

        Returns:
            Expression: The parsed map literal.
        """

    @abstractmethod
    def parse_entity_literal(self, template: str) -> EntityLiteral:
        """Parses an entity literal.

        Args:
            template (str): The template of the entity literal.

        Returns:
            EntityLiteral: The parsed entity literal.
        """

    @abstractmethod
    def parse_index_expression(self, array: Expression) -> IndexExpression:
        """Parses an array index expression.

        Args:
            array (Expression): The array being indexed.

        Returns:
            IndexExpression: The parsed index expression.
        """

    @abstractmethod
    def parse_pipe_expression(self, args: List[Expression]) -> Expression:
        """Parses a pipe expression.

        Args:
            args (List[Expression]): The arg list to be passed to the first function.

        Returns:
            Expression: The parsed pipe expression or array literal.
        """

    @abstractmethod
    def parse_member_access_expression(self, composite: Expression) -> Expression:
        """Parses an composite type member access expression.

        Args:
            composite (Expression): The composite being accessed.

        Returns:
            MemberAccessExpression: The parsed member access expression.
        """

    @abstractmethod
    def parse_method_call_expression(
        self, composite: Expression, method: Identifier
    ) -> MethodCallExpression:
        """Parses a method call expression.

        Args:
            composite (Expression): The composite containing the method.
            method (Identifier): The method being called.

        Returns:
            MethodCallExpression: The parsed method call expression.
        """


class StatementParserABC(Protocol):
    """Abstract base class for statement parsers."""

    expression_parser: ExpressionParserABC

    @abstractmethod
    def parse_statements(self) -> List[Statement]:
        """Iteratively parses statements until the end of the program.

        Returns:
            List[Statement]: A list of parsed statements.
        """

    @abstractmethod
    def parse_statement(self) -> Statement:
        """Parses a single statement based on the current token type.

        Returns:
            Statement: The parsed statement.
        """

    @abstractmethod
    def parse_expression_statement(self) -> ExpressionStatement:
        """Parses an expression statement.

        Returns:
            ExpressionStatement: The parsed expression statement.
        """

    @abstractmethod
    def parse_variable_declaration(self) -> VariableDeclaration:
        """Parses a variable declaration statement.

        Returns:
            VariableDeclaration: The parsed variable declaration.
        """

    @abstractmethod
    def parse_template_declaration(self) -> TemplateDeclaration:
        """Parses a template declaration statement.

        Returns:
            TemplateDeclaration: The parsed template declaration.
        """

    @abstractmethod
    def parse_entity_declaration(self) -> VariableDeclaration:
        """Parses an entity declaration statement.

        Returns:
            VariableDeclaration: The parsed entity declaration.

        Raises:
            SyntaxError: If the template identifier is not found.
        """

    @abstractmethod
    def parse_block_statement(self) -> BlockStatement:
        """Parses a block statement.

        Returns:
            BlockStatement: The parsed block statement.
        """

    @abstractmethod
    def parse_if_statement(self) -> IfStatement:
        """Parses an if statement.

        Returns:
            IfStatement: The parsed if statement.
        """

    @abstractmethod
    def parse_while_statement(self) -> WhileStatement:
        """Parses a while statement.

        Returns:
            WhileStatement: The parsed while statement.
        """

    @abstractmethod
    def parse_range_statement(self) -> RangeStatement:
        """Parses a range statement.

        Returns:
            RangeStatement: The parsed range statement.
        """

    @abstractmethod
    def parse_each_statement(self) -> EachStatement:
        """Parses an each statement.

        Returns:
            EachStatement: The parsed each statement.
        """

    @abstractmethod
    def parse_halt_statement(self) -> HaltStatement:
        """Parses a halt statement.

        Returns:
            HaltStatement: The parsed halt statement.
        """

    @abstractmethod
    def parse_skip_statement(self) -> SkipStatement:
        """Parses a skip statement.

        Returns:
            SkipStatement: The parsed skip statement.
        """

    @abstractmethod
    def parse_return_statement(self) -> ReturnStatement:
        """Parses a return statement.

        Returns:
            ReturnStatement: The parsed return statement.
        """

    @abstractmethod
    def parse_function_declaration(self) -> FunctionDeclaration:
        """Parses a function declaration statement.

        Returns:
            FunctionDeclaration: The parsed function declaration.
        """

    @abstractmethod
    def parse_echo_statement(self) -> EchoStatement:
        """Parses an echo statement.

        Returns:
            EchoStatement: The parsed echo statement.
        """


class ParserABC(ABC):
    """Abstract base class for program parsers."""

    statement_parser: StatementParserABC

    @abstractmethod
    def parse(self) -> Program:
        """Parses the tokens into a Program AST node.

        Returns:
            Program: The root node of the parsed AST.
        """

    @abstractmethod
    def consume(self, token_type: TokenType) -> Token:
        """Consumes the current token if it matches the expected type.

        Args:
            token_type (TokenType): The expected type of the current token.

        Returns:
            Token: The consumed token.

        Raises:
            SyntaxError: If the current token type does not match the expected type.
        """

    @abstractmethod
    def current(self) -> Token:
        """Retrieves the token at the current position.

        Returns:
            Token: The current token.

        Raises:
            RuntimeError: If the end of the token list is overrun.
        """

    @abstractmethod
    def is_eof(self) -> bool:
        """Checks if the current token is the end-of-file token.

        Returns:
            bool: True if the current token is EOF, otherwise False.
        """

    @abstractmethod
    def parse_var_type(self) -> VarType:
        """Parses a variable type.

        Returns:
            VarType: The parsed variable type.
        """

    @abstractmethod
    def parse_array_type(self, element_type: VarType) -> VarType:
        """Parses an array type.

        Args:
            element_type (VarType): The element type of the array.

        Returns:
            VarType: The parsed array type.
        """

    @abstractmethod
    def parse_set_or_map_type(self, element_type: VarType) -> VarType:
        """Parses a set or map type.

        Args:
            element_type (VarType): The element type of the set or map.

        Returns:
            VarType: The parsed set or map type.
        """

    @abstractmethod
    def parse_return_type(self) -> VarType:
        """Parses a return type for a function declaration.

        Returns:
            VarType: The parsed return type.
        """

    @abstractmethod
    def parse_function_type(self) -> FunctionType:
        """Parses a function type.

        Returns:
            FunctionType: The parsed function type.
        """
