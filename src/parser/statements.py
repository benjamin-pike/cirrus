from typing import *
from lexer.tokens import TokenType
from parser._types import ParserABC, StatementParserABC
from parser.expressions import ExpressionParser
from syntax.ast import (
    EchoStatement, Statement, ExpressionStatement, VariableDeclaration, BlockStatement, IfStatement,
    WhileStatement, RangeStatement, EachStatement, ReturnStatement, FunctionDeclaration,
    NumericLiteral
) 

class StatementParser(StatementParserABC):
    """
    The StatementParser class parses statements from a list of tokens using the provided parser.

    Attributes:
        parser (ParserABC): The main parser instance.
        expression_parser (ExpressionParser): An instance of ExpressionParser to handle expression parsing.
    """
    def __init__(self, parser: ParserABC) -> None:
        """
        Initialises the StatementParser with the main parser and initialises the expression parser.

        Args:
            parser (ParserABC): The main parser instance.
        """
        self.parser = parser
        self.expression_parser = ExpressionParser(parser)

    def parse_statements(self) -> List[Statement]:
        """
        Iteratively parses statements until the end of the file.

        Returns:
            List[Statement]: A list of parsed statements.
        """
        statements: List[Statement] = []
        while not self.parser.is_eof():
            statements.append(self.parse_statement())
        
        return statements

    def parse_statement(self) -> Statement:
        """
        Parses a single statement based on the current token type.

        Returns:
            Statement: The parsed statement.
        """
        current = self.parser.current()

        match current.type:
            case TokenType.LET:
                return self.parse_variable_declaration()
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
            case TokenType.RETURN:
                return self.parse_return_statement()
            case TokenType.FUNC:
                return self.parse_function_declaration()
            case TokenType.ECHO:
                return self.parse_echo_statement()
            case _:
                # Default to parsing an expression statement
                return self.parse_expression_statement()

    def parse_expression_statement(self) -> ExpressionStatement:
        """
        Parses an expression statement.

        Returns:
            ExpressionStatement: The parsed expression statement.
        """
        expr = self.expression_parser.parse_expression()
        self.parser.consume(TokenType.SEMICOLON)
        
        return ExpressionStatement(expr)

    def parse_variable_declaration(self) -> VariableDeclaration:
        """
        Parses a variable declaration statement.

        Returns:
            VariableDeclaration: The parsed variable declaration.
        """
        self.parser.consume(TokenType.LET)
        name = self.parser.consume(TokenType.IDENTIFIER)
        self.parser.consume(TokenType.ASSIGN)
        initializer = self.expression_parser.parse_expression()
        self.parser.consume(TokenType.SEMICOLON)
        
        return VariableDeclaration(name.value, initializer)

    def parse_block_statement(self) -> BlockStatement:
        """
        Parses a block statement.

        Returns:
            BlockStatement: The parsed block statement.
        """
        self.parser.consume(TokenType.LBRACE)
        
        statements: List[Statement] = []
        while self.parser.current().type != TokenType.RBRACE and not self.parser.is_eof():
            statements.append(self.parse_statement())
        
        self.parser.consume(TokenType.RBRACE)
        
        return BlockStatement(statements)

    def parse_if_statement(self) -> IfStatement:
        """
        Parses an if statement.

        Returns:
            IfStatement: The parsed if statement.
        """
        self.parser.consume(TokenType.IF) 
        condition = self.expression_parser.parse_expression()
        then_block = self.parse_block_statement()
 
        if self.parser.current().type == TokenType.ELSE:
            self.parser.consume(TokenType.ELSE)
            else_block = self.parse_block_statement()
        else:
            else_block = None
        
        return IfStatement(condition, then_block, else_block)

    def parse_while_statement(self) -> WhileStatement:
        """
        Parses a while statement.

        Returns:
            WhileStatement: The parsed while statement.
        """
        self.parser.consume(TokenType.WHILE)
        condition = self.expression_parser.parse_expression()
        body = self.parse_block_statement()
        
        return WhileStatement(condition, body)

    def parse_range_statement(self) -> RangeStatement:
        """
        Parses a range statement.

        Returns:
            RangeStatement: The parsed range statement.
        """
        self.parser.consume(TokenType.RANGE)
        identifier = self.parser.consume(TokenType.IDENTIFIER)
        self.parser.consume(TokenType.IN)
        start = self.expression_parser.parse_expression()
        self.parser.consume(TokenType.TO)
        end = self.expression_parser.parse_expression()
        
        if self.parser.current().type == TokenType.BY:
            self.parser.consume(TokenType.BY)
            increment = self.expression_parser.parse_expression()
        else:
            increment = NumericLiteral(1)
        
        body = self.parse_block_statement()
        
        return RangeStatement(identifier.value, start, end, increment, body)

    def parse_each_statement(self) -> EachStatement:
        """
        Parses an each statement.

        Returns:
            EachStatement: The parsed each statement.
        """
        self.parser.consume(TokenType.EACH)
        identifier = self.parser.consume(TokenType.IDENTIFIER)
        self.parser.consume(TokenType.IN)
        iterable = self.expression_parser.parse_expression()
        body = self.parse_block_statement()
        
        return EachStatement(identifier.value, iterable, body)

    def parse_return_statement(self) -> ReturnStatement:
        """
        Parses a return statement.

        Returns:
            ReturnStatement: The parsed return statement.
        """
        self.parser.consume(TokenType.RETURN)
        expr = self.expression_parser.parse_expression()
        self.parser.consume(TokenType.SEMICOLON)
        
        return ReturnStatement(expr)

    def parse_function_declaration(self) -> FunctionDeclaration:
        """
        Parses a function declaration statement.

        Returns:
            FunctionDeclaration: The parsed function declaration.
        """
        self.parser.consume(TokenType.FUNC)
        name = self.parser.consume(TokenType.IDENTIFIER)
        self.parser.consume(TokenType.ASSIGN)
        self.parser.consume(TokenType.LBRACKET)
        
        parameters: List[str] = []
        if self.parser.current().type != TokenType.RBRACKET:
            parameters.append(self.parser.consume(TokenType.IDENTIFIER).value)
            while self.parser.current().type == TokenType.COMMA:
                self.parser.consume(TokenType.COMMA)
                parameters.append(self.parser.consume(TokenType.IDENTIFIER).value)
        
        self.parser.consume(TokenType.RBRACKET)
        self.parser.consume(TokenType.ARROW)
        body = self.parse_block_statement()
        
        return FunctionDeclaration(name.value, parameters, body)
    
    def parse_echo_statement(self) -> EchoStatement:
        """
        Parses an echo statement.

        Returns:
            EchoStatement: The parsed echo statement.
        """
        self.parser.consume(TokenType.ECHO)
        expr = self.expression_parser.parse_expression()
        self.parser.consume(TokenType.SEMICOLON)
        
        return EchoStatement(expr)