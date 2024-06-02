from typing import *
from lexer.tokens import TokenType
from parser.helpers import get_precedence
from parser._types import ParserABC, ExpressionParserABC
from syntax.ast import (
    Expression, AssignmentExpression, Identifier, BinaryExpression, StringLiteral,
    UnaryExpression, NumericLiteral, CallExpression, ArrayLiteral, IndexExpression
)

class ExpressionParser(ExpressionParserABC):
    """
    The ExpressionParser class parses expressions from a list of tokens using the provided parser.

    Attributes:
        parser (ParserABC): The main parser instance.
    """
    def __init__(self, parser: ParserABC) -> None:
        """
        Initialises the ExpressionParser with the main parser instance.

        Args:
            parser (ParserABC): The main parser instance.
        """
        self.parser = parser

    def parse_expression(self) -> Expression:
        """
        Parses a general expression. Initially starts with parsing an assignment expression.

        Returns:
            Expression: The parsed expression.
        """
        return self.parse_assignment_expression()

    def parse_assignment_expression(self) -> Expression:
        """
        Parses an assignment expression.
        If the current token is not an assignment operator, it returns the result of parse_binary_expression.

        Returns:
            Expression: The parsed assignment expression or the result of parse_binary_expression.
            
        Raises:
            SyntaxError: If the left-hand side of the assignment is not a valid identifier or index expression.
        """
        left = self.parse_binary_expression()
        
        if self.parser.current().type == TokenType.ASSIGN:
            self.parser.consume(TokenType.ASSIGN)
            right = self.parse_assignment_expression()
            
            if isinstance(left, (Identifier, IndexExpression)):
                return AssignmentExpression(left, right)
            else:
                raise SyntaxError('Invalid left-hand side in assignment')
        
        return left

    def parse_binary_expression(self, precedence: int = 0) -> Expression:
        """
        Parses a binary expression using operator precedence.
        If the current token does not have higher precedence, it delegates to parse_unary_expression.

        Args:
            precedence (int): The current precedence level.

        Returns:
            Expression: The parsed binary expression or the result of parse_unary_expression.
        """
        left = self.parse_unary_expression()
        
        while not self.parser.is_eof():
            current_precedence = get_precedence(self.parser.current().type)
            
            if current_precedence <= precedence:
                break
            
            operator = self.parser.current().type
            self.parser.consume(operator)
            right = self.parse_binary_expression(current_precedence)
            left = BinaryExpression(left, operator, right)
        
        return left

    def parse_unary_expression(self) -> Expression:
        """
        Parses a unary expression, handling prefix and postfix operators. 
        For other types of expressions, it delegates to parse_primary_expression.

        Returns:
            Expression: The parsed unary expression or the result of parse_primary_expression.
        """
        token = self.parser.current()
        
        # Prefix unary operators
        if token.type in {TokenType.INCREMENT, TokenType.DECREMENT}:
            self.parser.consume(token.type)
            operand = self.parse_unary_expression()
            return UnaryExpression(token.type, operand, 'PRE')
        
        expr = self.parse_primary_expression()

        # Postfix unary operators
        while self.parser.current().type in {TokenType.INCREMENT, TokenType.DECREMENT}:
            operator = self.parser.current().type
            self.parser.consume(operator)
            expr = UnaryExpression(operator, expr, 'POST')
        
        return expr

    def parse_primary_expression(self) -> Expression:
        """
        Parses a primary expression, which can be literals, identifiers, or grouped expressions.
        Delegates to...
            - parse_identifier_expression if the current token is an identifier.
            - parse_expression if the current token is a left parenthesis.
            - parse_array_literal if the current token is a left bracket.

        Returns:
            Expression: The parsed primary expression.
        
        Raises:
            SyntaxError: If the current token is not a valid primary expression.
        """
        token = self.parser.current()

        match token.type:
            case TokenType.INT:
                self.parser.consume(TokenType.INT)
                return NumericLiteral(int(token.value))
            case TokenType.SINGLE_QUOTE:
                self.parser.consume(TokenType.SINGLE_QUOTE)
                str_token = self.parser.consume(TokenType.STRING)
                self.parser.consume(TokenType.SINGLE_QUOTE)
                return StringLiteral(str_token.value)
            case TokenType.DOUBLE_QUOTE:
                self.parser.consume(TokenType.DOUBLE_QUOTE)
                str_token = self.parser.consume(TokenType.STRING)
                self.parser.consume(TokenType.DOUBLE_QUOTE)
                return StringLiteral(str_token.value)
            case TokenType.IDENTIFIER:
                return self.parse_identifier_expression()
            case TokenType.LPAREN:
                self.parser.consume(TokenType.LPAREN)
                expr = self.parse_expression()
                self.parser.consume(TokenType.RPAREN)
                return expr
            case TokenType.LBRACKET:
                return self.parse_array_literal()
            case _:
                raise SyntaxError(f'Unexpected token {token}')

    def parse_identifier_expression(self) -> Expression:
        """
        Parses an identifier expression, which can be a variable, function call, or array index.
        Delegates to...
            - parse_call_expression if the identifier is followed by a parenthesis 
            - parse_index_expression if the identifier is followed by a bracket.

        Returns:
            Expression: The parsed identifier, call expression, or index expression.
        """
        identifier = self.parser.current().value
        self.parser.consume(TokenType.IDENTIFIER)
        
        if self.parser.current().type == TokenType.LPAREN:
            return self.parse_call_expression(Identifier(identifier))
        if self.parser.current().type == TokenType.LBRACKET:
            return self.parse_index_expression(Identifier(identifier))
        
        return Identifier(identifier)

    def parse_call_expression(self, callee: Identifier) -> CallExpression:
        """
        Parses a function call expression.

        Args:
            callee (Identifier): The function being called.

        Returns:
            CallExpression: The parsed call expression.
        """
        self.parser.consume(TokenType.LPAREN)
        arguments = self.parse_arguments()
        self.parser.consume(TokenType.RPAREN)
       
        return CallExpression(callee, arguments)

    def parse_arguments(self) -> List[Expression]:
        """
        Parses the arguments of a function call.

        Returns:
            List[Expression]: The list of parsed arguments.
        """
        args: List[Expression] = []
        if self.parser.current().type != TokenType.RPAREN:
            args.append(self.parse_expression())
            while self.parser.current().type == TokenType.COMMA:
                self.parser.consume(TokenType.COMMA)
                args.append(self.parse_expression())
        
        return args
    
    def parse_array_literal(self) -> ArrayLiteral:
        """
        Parses an array literal.

        Returns:
            ArrayLiteral: The parsed array literal.
        """
        self.parser.consume(TokenType.LBRACKET)
        elements: List[Expression] = []
        
        if self.parser.current().type != TokenType.RBRACKET:
            elements.append(self.parse_expression())
            while self.parser.current().type == TokenType.COMMA:
                self.parser.consume(TokenType.COMMA)
                elements.append(self.parse_expression())
        
        self.parser.consume(TokenType.RBRACKET)
        
        return ArrayLiteral(elements)

    def parse_index_expression(self, array: Expression) -> IndexExpression:
        """
        Parses an index expression for array access.

        Args:
            array (Expression): The array being indexed.

        Returns:
            IndexExpression: The parsed index expression.
        """
        self.parser.consume(TokenType.LBRACKET)
        index = self.parse_expression()
        self.parser.consume(TokenType.RBRACKET)
        
        return IndexExpression(array, index)