from typing import List, Optional
from frontend.lexer.tokens import TokenType
from frontend.parser.helpers import get_precedence
from frontend.parser.typing import ExpressionParserABC, ParserABC
from frontend.syntax.ast import *


class ExpressionParser(ExpressionParserABC):
    """Parses AST expression nodes from a list of tokens."""

    def __init__(self, parser: ParserABC) -> None:
        self.parser = parser

    def parse_expression(self) -> Expression:
        if self.parser.current().token_type == TokenType.LBRACKET:
            return self.parse_array_literal()
        if self.parser.current().token_type == TokenType.LBRACE:
            return self.parse_set_literal()
        if self.parser.current().token_type == TokenType.FUNC:
            return self.parse_function_literal()

        return self.parse_assignment_expression()

    def parse_assignment_expression(self) -> Expression:
        left = self.parse_binary_expression()

        if self.parser.current().token_type == TokenType.ASSIGN:
            self.parser.consume(TokenType.ASSIGN)
            right = self.parse_assignment_expression()

            if isinstance(left, (Identifier, IndexExpression, MemberAccessExpression)):
                return AssignmentExpression(left, right)

            raise SyntaxError("Invalid left-hand side in assignment")

        return left

    def parse_binary_expression(self, precedence: int = 0) -> Expression:
        left = self.parse_unary_expression()

        while not self.parser.is_eof():
            current_precedence = get_precedence(self.parser.current().token_type)

            if current_precedence <= precedence:
                break

            operator = self.parser.current().token_type

            self.parser.consume(operator)
            right = self.parse_binary_expression(current_precedence)
            left = BinaryExpression(left, operator, right)

        return left

    def parse_unary_expression(self) -> Expression:
        token = self.parser.current()

        # Prefix unary operators
        if token.token_type in {
            TokenType.INCREMENT,
            TokenType.DECREMENT,
            TokenType.LOGICAL_NOT,
            TokenType.MINUS,
        }:
            self.parser.consume(token.token_type)
            operand = self.parse_unary_expression()
            return UnaryExpression(token.token_type, operand, "PRE")

        expr = self.parse_primary_expression()

        # Postfix unary operators
        while self.parser.current().token_type in {
            TokenType.INCREMENT,
            TokenType.DECREMENT,
        }:
            operator = self.parser.current().token_type
            self.parser.consume(operator)
            expr = UnaryExpression(operator, expr, "POST")

        return expr

    def parse_primary_expression(self) -> Expression:
        token = self.parser.current()

        match token.token_type:
            case TokenType.INT_LITERAL:
                self.parser.consume(TokenType.INT_LITERAL)
                return NumericLiteral(int(token.value))
            case TokenType.FLOAT_LITERAL:
                self.parser.consume(TokenType.FLOAT_LITERAL)
                return NumericLiteral(float(token.value))
            case TokenType.SINGLE_QUOTE | TokenType.DOUBLE_QUOTE:
                self.parser.consume(token.token_type)
                str_token = self.parser.consume(TokenType.STRING_LITERAL)
                self.parser.consume(token.token_type)
                return StringLiteral(str_token.value)
            case TokenType.BOOLEAN_LITERAL:
                self.parser.consume(TokenType.BOOLEAN_LITERAL)
                return BooleanLiteral(token.value == "true")

            case TokenType.LPAREN:
                self.parser.consume(TokenType.LPAREN)
                expr = self.parse_expression()
                self.parser.consume(TokenType.RPAREN)
                return expr
            case TokenType.LBRACKET:
                return self.parse_array_literal()
            case TokenType.LBRACE:
                return self.parse_set_literal()

            case TokenType.IDENTIFIER:
                return self.parse_identifier_expression()

            case _:
                raise SyntaxError(f"Unexpected token {token}")

    def parse_identifier_expression(self) -> Expression:
        identifier = self.parser.consume(TokenType.IDENTIFIER).value
        expr = Identifier(identifier)
        if self.parser.current().token_type == TokenType.LBRACE:
            return self.parse_entity_literal(identifier)
        return self._parse_postfix_expression(expr)

    def parse_function_literal(self) -> FunctionLiteral:
        self.parser.consume(TokenType.FUNC)
        self.parser.consume(TokenType.LBRACKET)

        parameters: List[Tuple[str, VarType]] = []
        while self.parser.current().token_type != TokenType.RBRACKET:
            var_type = self.parser.parse_var_type()
            name = self.parser.consume(TokenType.IDENTIFIER).value
            parameters.append((name, var_type))
            if self.parser.current().token_type == TokenType.COMMA:
                self.parser.consume(TokenType.COMMA)

        self.parser.consume(TokenType.RBRACKET)
        self.parser.consume(TokenType.ARROW)
        body = self.parser.statement_parser.parse_block_statement()

        return FunctionLiteral(parameters, body)

    def parse_function_call_expression(
        self, callee: Expression
    ) -> FunctionCallExpression:
        self.parser.consume(TokenType.LPAREN)
        arguments = self.parse_arguments()
        self.parser.consume(TokenType.RPAREN)

        return FunctionCallExpression(callee, arguments)

    def parse_arguments(self) -> List[Expression]:
        args: List[Expression] = []
        if self.parser.current().token_type != TokenType.RPAREN:
            args.append(self.parse_expression())
            while self.parser.current().token_type == TokenType.COMMA:
                self.parser.consume(TokenType.COMMA)
                args.append(self.parse_expression())

        return args

    def parse_array_literal(self) -> Expression:
        self.parser.consume(TokenType.LBRACKET)
        elements: List[Expression] = []

        if self.parser.current().token_type != TokenType.RBRACKET:
            elements.append(self.parse_expression())
            while self.parser.current().token_type == TokenType.COMMA:
                self.parser.consume(TokenType.COMMA)
                elements.append(self.parse_expression())
        self.parser.consume(TokenType.RBRACKET)

        return self.parse_pipe_expression(elements)

    def parse_set_literal(self) -> Expression:
        self.parser.consume(TokenType.LBRACE)
        elements: List[Expression] = []

        if self.parser.current().token_type != TokenType.RBRACE:
            first_element = self.parse_expression()
            if self.parser.current().token_type == TokenType.COLON:
                return self.parse_map_literal(first_element)
            elements.append(first_element)
            while self.parser.current().token_type == TokenType.COMMA:
                self.parser.consume(TokenType.COMMA)
                elements.append(self.parse_expression())

        self.parser.consume(TokenType.RBRACE)

        return SetLiteral(elements)

    def parse_map_literal(self, first_key: Expression) -> Expression:
        elements: List[Tuple[Expression, Expression]] = []
        self.parser.consume(TokenType.COLON)
        elements.append((first_key, self.parse_expression()))

        while self.parser.current().token_type == TokenType.COMMA:
            self.parser.consume(TokenType.COMMA)
            key = self.parse_expression()
            self.parser.consume(TokenType.COLON)
            value = self.parse_expression()
            elements.append((key, value))

        self.parser.consume(TokenType.RBRACE)

        return MapLiteral(elements)

    def parse_entity_literal(self, template: str) -> EntityLiteral:
        self.parser.consume(TokenType.LBRACE)

        attributes: Dict[str, Expression] = {}
        while self.parser.current().token_type != TokenType.RBRACE:
            member = self.parser.consume(TokenType.IDENTIFIER)
            self.parser.consume(TokenType.COLON)
            initializer = self.parse_expression()
            if self.parser.current().token_type == TokenType.COMMA:
                self.parser.consume(TokenType.COMMA)

            attributes[member.value] = initializer

        self.parser.consume(TokenType.RBRACE)

        return EntityLiteral(CustomTypeIdentifier(template), attributes)

    def parse_index_expression(self, array: Expression) -> IndexExpression:
        self.parser.consume(TokenType.LBRACKET)
        index = self.parse_expression()
        self.parser.consume(TokenType.RBRACKET)

        return IndexExpression(array, index)

    def parse_pipe_expression(self, args: List[Expression]) -> Expression:
        call: Optional[FunctionCallExpression] = None

        while (
            not self.parser.is_eof()
            and self.parser.current().token_type == TokenType.ARROW
        ):
            self.parser.consume(TokenType.ARROW)
            identifier = self.parser.consume(TokenType.IDENTIFIER).value
            new_args: List[Expression] = [call] if call else args

            if self.parser.current().token_type == TokenType.LPAREN:
                self.parser.consume(TokenType.LPAREN)
                new_args.extend(self.parse_arguments())
                self.parser.consume(TokenType.RPAREN)

            call = FunctionCallExpression(Identifier(identifier), new_args)

        if call is None:
            return ArrayLiteral(args)

        return call

    def parse_member_access_expression(self, composite: Expression) -> Expression:
        self.parser.consume(TokenType.DOT)
        member = self.parser.consume(TokenType.IDENTIFIER)

        if self.parser.current().token_type == TokenType.LPAREN:
            return self.parse_method_call_expression(
                composite, Identifier(member.value)
            )

        return MemberAccessExpression(composite, Identifier(member.value))

    def parse_method_call_expression(
        self, composite: Expression, method: Identifier
    ) -> MethodCallExpression:
        self.parser.consume(TokenType.LPAREN)
        args = self.parse_arguments()
        self.parser.consume(TokenType.RPAREN)

        return MethodCallExpression(composite, method, args)

    def _parse_postfix_expression(self, expr: Expression) -> Expression:
        while True:
            match self.parser.current().token_type:
                case TokenType.LPAREN:
                    expr = self.parse_function_call_expression(expr)
                case TokenType.LBRACKET:
                    expr = self.parse_index_expression(expr)
                case TokenType.DOT:
                    expr = self.parse_member_access_expression(expr)
                case _:
                    break

        return expr
