from typing import List, Optional
from frontend.lexer.tokens import TokenType
from frontend.parser.helpers import get_precedence
from frontend.parser.typing import ExpressionParserABC, ParserABC
from frontend.syntax.ast import *


class ExpressionParser(ExpressionParserABC):
    """
    The ExpressionParser class parses expressions
    from a list of tokens using the provided parser.

    Attributes:
        parser (ParserABC): The main parser instance.
    """

    def __init__(self, parser: ParserABC) -> None:
        """Initialises the ExpressionParser with the main parser instance.

        Args:
            parser (ParserABC): The main parser instance.
        """
        self.parser = parser

    def parse_expression(self) -> Expression:
        """Parses a general expression.

        Returns:
            Expression: The parsed expression.
        """
        if self.parser.current().token_type == TokenType.LBRACKET:
            return self.parse_array_literal()
        if self.parser.current().token_type == TokenType.LBRACE:
            return self.parse_set_literal()
        if self.parser.current().token_type == TokenType.FUNC:
            return self.parse_function_literal()

        return self.parse_assignment_expression()

    def parse_assignment_expression(self) -> Expression:
        """Parses an assignment expression.
        If the current token is not an assignment operator,
        it returns the result of parse_binary_expression.

        Returns:
            Expression: The parsed assignment expression
            or the result of parse_binary_expression.

        Raises:
            SyntaxError: If the left-hand side of the assignment
            is not a valid identifier or index expression.
        """
        left = self.parse_binary_expression()

        if self.parser.current().token_type == TokenType.ASSIGN:
            self.parser.consume(TokenType.ASSIGN)
            right = self.parse_assignment_expression()

            if isinstance(left, (Identifier, IndexExpression)):
                return AssignmentExpression(left, right)

            raise SyntaxError("Invalid left-hand side in assignment")

        return left

    def parse_binary_expression(self, precedence: int = 0) -> Expression:
        """Parses a binary expression using operator precedence.
        If the current token does not have higher precedence,
        it delegates to parse_unary_expression.

        Args:
            precedence (int): The current precedence level.

        Returns:
            Expression: The parsed binary expression
            or the result of parse_unary_expression.
        """
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
        """Parses a unary expression, handling prefix and postfix operators.
        For other types of expressions, it delegates to parse_primary_expression.

        Returns:
            Expression: The parsed unary expression
            or the result of parse_primary_expression.
        """
        token = self.parser.current()

        # Prefix unary operators
        if token.token_type in {
            TokenType.INCREMENT,
            TokenType.DECREMENT,
            TokenType.LOGICAL_NOT,
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
        """Parses a primary expression, which can be
        literals, identifiers, or grouped expressions.
        Delegates to...
            - parse_identifier_expression if the current token is an identifier.
            - parse_expression if the current token is a left parenthesis.
            - parse_array_literal if the current token is a left bracket.
            - parse_set_literal if the current token is a left brace.

        Returns:
            Expression: The parsed primary expression.

        Raises:
            SyntaxError: If the current token is not a valid primary expression.
        """
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
        """Parses an identifier expression, which can
        be a variable, function call, or array index.
        Delegates to...
            - parse_method_call_expression if followed by a parenthesis.
            - parse_member_access_expression if followed by a dot.

        Returns:
            Expression: The parsed identifier, call expression, or index expression.
        """
        identifier = self.parser.consume(TokenType.IDENTIFIER).value
        expr = Identifier(identifier)
        if self.parser.current().token_type == TokenType.LBRACE:
            return self.parse_entity_literal(identifier)
        return self.parse_postfix_expression(expr)

    def parse_function_literal(self) -> FunctionLiteral:
        """Parses a function expression
        Delegates to parse_array_literal if a type followed by an expression is present.

        Returns:
            Expression: The parsed function expression.
        """
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
        """Parses a function function call expression.

        Args:
            callee (Expression): The function being called.

        Returns:
            FunctionCallExpression: The parsed function call expression.
        """
        self.parser.consume(TokenType.LPAREN)
        arguments = self.parse_arguments()
        self.parser.consume(TokenType.RPAREN)

        return FunctionCallExpression(callee, arguments)

    def parse_arguments(self) -> List[Expression]:
        """Parses the arguments of a function call.

        Returns:
            List[Expression]: The list of parsed arguments.
        """
        args: List[Expression] = []
        if self.parser.current().token_type != TokenType.RPAREN:
            args.append(self.parse_expression())
            while self.parser.current().token_type == TokenType.COMMA:
                self.parser.consume(TokenType.COMMA)
                args.append(self.parse_expression())

        return args

    def parse_array_literal(self) -> Expression:
        """Parses an array literal.
        Delegates to parse_pipe_expression to handle cases
        where the array is followed by a pipe expression.

        Returns:
            Expression: The parsed array literal or a parsed pipe expression.
        """
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
        """Parses a set literal or delegates to parse_map_literal if colons are present.

        Returns:
            Expression: The parsed set literal or map literal.
        """
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
        """Parses an map literal

        Args:
            first_key (Expression): The first key in the map literal.

        Returns:
            Expression: The parsed map literal.
        """
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

    def parse_entity_literal(self, template: str) -> Expression:
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

        return EntityLiteral(CustomType(template), attributes)

    def parse_index_expression(self, array: Expression) -> IndexExpression:
        """Parses an index expression for array access.

        Args:
            array (Expression): The array being indexed.

        Returns:
            IndexExpression: The parsed index expression.
        """
        self.parser.consume(TokenType.LBRACKET)
        index = self.parse_expression()
        self.parser.consume(TokenType.RBRACKET)

        return IndexExpression(array, index)

    def parse_pipe_expression(self, args: List[Expression]) -> Expression:
        """Parses a pipe expression beginning with a parameter list.

        Args:
            args (List[Expression]):
                The list of args to be passed to the first function.

        Returns:
            Expression: The parsed pipe expression.
        """
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

    def parse_postfix_expression(self, expr: Expression) -> Expression:
        """Parses the postfix expressions for member access and method calls.

        Args:
            expr (Expression): The initial expression to be extended.

        Returns:
            Expression: The extended expression with member accesses and method calls.
        """
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

    def parse_member_access_expression(self, obj: Expression) -> Expression:
        """Parses a member expression for object access.
        Delegate to parse_method_call_expression
        if the member is followed by a parenthesis.

        Args:
            obj (Expression): The object being accessed.

        Returns:
            MemberAccessExpression: The parsed member access expression.
        """
        self.parser.consume(TokenType.DOT)
        member = self.parser.consume(TokenType.IDENTIFIER)

        if self.parser.current().token_type == TokenType.LPAREN:
            return self.parse_method_call_expression(obj, Identifier(member.value))

        return MemberAccessExpression(obj, Identifier(member.value))

    def parse_method_call_expression(
        self, obj: Expression, method: Identifier
    ) -> MethodCallExpression:
        """Parses a method call expression.

        Args:
            obj (Expression): The object being called.

        Returns:
            MethodCallExpression: The parsed method call expression.
        """
        self.parser.consume(TokenType.LPAREN)
        args = self.parse_arguments()
        self.parser.consume(TokenType.RPAREN)

        return MethodCallExpression(obj, method, args)
