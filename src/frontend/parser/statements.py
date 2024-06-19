from typing import List, Tuple
from frontend.parser.typing import ParserABC, StatementParserABC
from frontend.parser.expressions import ExpressionParser
from frontend.lexer.tokens import TokenType
from frontend.semantic.types import *
from frontend.syntax.ast import *


class StatementParser(StatementParserABC):
    """
    The StatementParser class parses statements from
    a list of tokens using the provided parser.

    Attributes:
        parser (ParserABC): The main parser instance.
        expression_parser (ExpressionParser):
            An instance of ExpressionParser to handle expression parsing.
    """

    def __init__(self, parser: ParserABC) -> None:
        """Initialises the StatementParser with the main
        parser and initialises the expression parser.

        Args:
            parser (ParserABC): The main parser instance.
        """
        self.parser = parser
        self.expression_parser = ExpressionParser(parser)

    def parse_statements(self) -> List[Statement]:
        """Iteratively parses statements until the end of the program.

        Returns:
            List[Statement]: A list of parsed statements.
        """
        statements: List[Statement] = []
        while not self.parser.is_eof():
            statements.append(self.parse_statement())

        return statements

    def parse_statement(self) -> Statement:
        """Parses a single statement based on the current token type.

        Returns:
            Statement: The parsed statement.
        """
        current = self.parser.current()

        match current.token_type:
            case (
                TokenType.INT
                | TokenType.FLOAT
                | TokenType.STR
                | TokenType.BOOL
                | TokenType.INFER
            ):
                return self.parse_variable_declaration()
            case TokenType.ENTITY:
                return self.parse_entity_declaration()
            case TokenType.LBRACE:
                return self.parse_block_statement()
            case TokenType.IF:
                return self.parse_if_statement()
            case TokenType.WHILE:
                return self.parse_while_statement()
            case TokenType.RANGE:
                return self.parse_range_statement()
            case TokenType.EACH:
                return self.parse_each_statement()
            case TokenType.HALT:
                return self.parse_halt_statement()
            case TokenType.SKIP:
                return self.parse_skip_statement()
            case TokenType.FUNC:
                return self.parse_function_declaration()
            case TokenType.RETURN:
                return self.parse_return_statement()
            case TokenType.ECHO:
                return self.parse_echo_statement()
            case TokenType.TEMPLATE:
                return self.parse_template_declaration()
            case _:
                # Default to parsing an expression statement
                return self.parse_expression_statement()

    def parse_expression_statement(self) -> ExpressionStatement:
        """Parses an expression statement.

        Returns:
            ExpressionStatement: The parsed expression statement.
        """
        expr = self.expression_parser.parse_expression()
        self.parser.consume(TokenType.SEMICOLON)

        return ExpressionStatement(expr)

    def parse_variable_declaration(self) -> VariableDeclaration:
        """Parses a variable declaration statement.

        Returns:
            VariableDeclaration: The parsed variable declaration.
        """
        var_type = self.parser.parse_var_type()
        name = self.parser.consume(TokenType.IDENTIFIER)
        self.parser.consume(TokenType.ASSIGN)
        initializer = self.expression_parser.parse_expression()
        self.parser.consume(TokenType.SEMICOLON)

        return VariableDeclaration(name.value, var_type, initializer)

    def parse_entity_declaration(self) -> VariableDeclaration:
        """Parses an entity declaration statement.

        Returns:
            VariableDeclaration: The parsed entity declaration.

        Raises:
            SyntaxError: If the template identifier is not found.
        """
        self.parser.consume(TokenType.ENTITY)
        name = self.parser.consume(TokenType.IDENTIFIER)
        self.parser.consume(TokenType.ASSIGN)

        if not self.parser.current().token_type == TokenType.IDENTIFIER:
            raise SyntaxError(
                f"Expected template identifier, got {self.parser.current().value}"
            )

        template = self.parser.consume(TokenType.IDENTIFIER).value
        initializer = self.expression_parser.parse_entity_literal(template)
        self.parser.consume(TokenType.SEMICOLON)

        return VariableDeclaration(name.value, CustomType(template), initializer)

    def parse_block_statement(self) -> BlockStatement:
        """Parses a block statement.

        Returns:
            BlockStatement: The parsed block statement.
        """
        self.parser.consume(TokenType.LBRACE)

        statements: List[Statement] = []
        while (
            self.parser.current().token_type != TokenType.RBRACE
            and not self.parser.is_eof()
        ):
            statements.append(self.parse_statement())

        self.parser.consume(TokenType.RBRACE)

        return BlockStatement(statements)

    def parse_if_statement(self) -> IfStatement:
        """Parses an if statement.

        Returns:
            IfStatement: The parsed if statement.
        """
        self.parser.consume(TokenType.IF)
        self.parser.consume(TokenType.LPAREN)
        condition = self.expression_parser.parse_expression()
        self.parser.consume(TokenType.RPAREN)
        then_block = self.parse_block_statement()

        if self.parser.current().token_type == TokenType.ELSE:
            self.parser.consume(TokenType.ELSE)
            else_block = self.parse_block_statement()
        else:
            else_block = None

        return IfStatement(condition, then_block, else_block)

    def parse_while_statement(self) -> WhileStatement:
        """Parses a while statement.

        Returns:
            WhileStatement: The parsed while statement.
        """
        self.parser.consume(TokenType.WHILE)
        self.parser.consume(TokenType.LPAREN)
        condition = self.expression_parser.parse_expression()
        self.parser.consume(TokenType.RPAREN)
        body = self.parse_block_statement()

        return WhileStatement(condition, body)

    def parse_range_statement(self) -> RangeStatement:
        """Parses a range statement.

        Returns:
            RangeStatement: The parsed range statement.
        """
        self.parser.consume(TokenType.RANGE)
        self.parser.consume(TokenType.LPAREN)
        identifier = self.parser.consume(TokenType.IDENTIFIER)
        self.parser.consume(TokenType.IN)
        start = self.expression_parser.parse_expression()
        self.parser.consume(TokenType.TO)
        end = self.expression_parser.parse_expression()

        if self.parser.current().token_type == TokenType.BY:
            self.parser.consume(TokenType.BY)
            increment = self.expression_parser.parse_expression()
        else:
            increment = NumericLiteral(1)

        self.parser.consume(TokenType.RPAREN)

        body = self.parse_block_statement()

        return RangeStatement(identifier.value, start, end, increment, body)

    def parse_each_statement(self) -> EachStatement:
        """Parses an each statement.

        Returns:
            EachStatement: The parsed each statement.
        """
        self.parser.consume(TokenType.EACH)
        self.parser.consume(TokenType.LPAREN)
        identifier = self.parser.consume(TokenType.IDENTIFIER)
        self.parser.consume(TokenType.IN)
        iterable = self.expression_parser.parse_expression()
        self.parser.consume(TokenType.RPAREN)
        body = self.parse_block_statement()

        return EachStatement(identifier.value, iterable, body)

    def parse_halt_statement(self) -> HaltStatement:
        """Parses a halt statement.

        Returns:
            HaltStatement: The parsed halt statement.
        """
        self.parser.consume(TokenType.HALT)
        self.parser.consume(TokenType.SEMICOLON)

        return HaltStatement()

    def parse_skip_statement(self) -> SkipStatement:
        """Parses a skip statement.

        Returns:
            SkipStatement: The parsed skip statement.
        """
        self.parser.consume(TokenType.SKIP)
        self.parser.consume(TokenType.SEMICOLON)

        return SkipStatement()

    def parse_return_statement(self) -> ReturnStatement:
        """Parses a return statement.

        Returns:
            ReturnStatement: The parsed return statement.
        """
        self.parser.consume(TokenType.RETURN)

        expr = None
        if self.parser.current().token_type != TokenType.SEMICOLON:
            expr = self.expression_parser.parse_expression()

        self.parser.consume(TokenType.SEMICOLON)

        return ReturnStatement(expr)

    def parse_function_declaration(self) -> FunctionDeclaration:
        """Parses a function declaration statement.

        Returns:
            FunctionDeclaration: The parsed function declaration.
        """
        self.parser.consume(TokenType.FUNC)
        name = self.parser.consume(TokenType.IDENTIFIER)
        self.parser.consume(TokenType.RETURN_ARROW)
        return_type = self.parser.parse_return_type()
        self.parser.consume(TokenType.ASSIGN)
        self.parser.consume(TokenType.LBRACKET)

        parameters: List[Tuple[str, VarType]] = []
        if self.parser.current().token_type != TokenType.RBRACKET:
            var_type = self.parser.parse_var_type()
            identifier = self.parser.consume(TokenType.IDENTIFIER).value
            parameters.append((identifier, var_type))

            while self.parser.current().token_type == TokenType.COMMA:
                self.parser.consume(TokenType.COMMA)
                var_type = self.parser.parse_var_type()
                identifier = self.parser.consume(TokenType.IDENTIFIER).value
                parameters.append((identifier, var_type))

        self.parser.consume(TokenType.RBRACKET)
        self.parser.consume(TokenType.ARROW)
        body = self.parse_block_statement()

        return FunctionDeclaration(
            name.value, FunctionType(return_type, parameters), body
        )

    def parse_echo_statement(self) -> EchoStatement:
        """Parses an echo statement.

        Returns:
            EchoStatement: The parsed echo statement.
        """
        self.parser.consume(TokenType.ECHO)
        expr = self.expression_parser.parse_expression()
        self.parser.consume(TokenType.SEMICOLON)

        return EchoStatement(expr)

    def parse_template_declaration(self) -> TemplateDeclaration:
        """Parses a template declaration statement.

        Returns:
            TemplateDeclaration: The parsed template declaration.
        """
        self.parser.consume(TokenType.TEMPLATE)
        name = self.parser.consume(TokenType.IDENTIFIER)
        self.parser.consume(TokenType.ASSIGN)
        self.parser.consume(TokenType.LBRACE)

        attributes: Dict[str, VarType] = {}
        methods: Dict[str, FunctionDeclaration] = {}
        while self.parser.current().token_type != TokenType.RBRACE:
            if self.parser.current().token_type == TokenType.FUNC:
                func = self.parse_function_declaration()
                methods[func.name] = func
            else:
                var_type = self.parser.parse_var_type()
                identifier = self.parser.consume(TokenType.IDENTIFIER).value
                self.parser.consume(TokenType.SEMICOLON)
                attributes[identifier] = var_type

        self.parser.consume(TokenType.RBRACE)
        self.parser.consume(TokenType.SEMICOLON)

        return TemplateDeclaration(name.value, attributes, methods)
