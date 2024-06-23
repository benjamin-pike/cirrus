from typing import *
from frontend.lexer.tokens import TokenType
from frontend.semantic.expressions import ExpressionAnalyzer
from frontend.semantic.statements import StatementAnalyzer
from frontend.semantic.symbol import SymbolTable
from frontend.semantic.types import PrimitiveType, VarType, VoidType
from frontend.semantic.typing import SemanticAnalyzerABC
from frontend.syntax.ast import *
from lib.helpers import is_iterable, pascal_to_snake_case


class SemanticAnalyzer(SemanticAnalyzerABC):
    """
    The SemanticAnalyzer class performs semantic analysis
    by traversing the AST and ensuring that:\n
        1) All variables and functions are declared before use.\n
        2) Variables and functions are not redeclared or shadowed in lower scopes.\n
        3) Types are compatible in declarations, expressions, and assignments.\n
        4) All code is reachable and flow control statements are used correctly.\n
    """

    def __init__(self) -> None:
        self.symbol_table = SymbolTable()
        self.statement_analyzer = StatementAnalyzer(self)
        self.expression_analyzer = ExpressionAnalyzer(self)

    def analyze(self, node: Node) -> VarType:
        """Analyses a node in the AST.

        Args:
            node (Node): The AST node to analyse.

        Returns:
            VarType: The type of the node.

        Raises:
            SyntaxError: If unreachable code is detected.
        """
        if not self.symbol_table.is_reachable():
            raise SyntaxError(f"Unreachable code detected at {node}")

        method_name = f"analyze_{pascal_to_snake_case(type(node).__name__)}"

        analyzer = self
        if isinstance(node, Statement):
            analyzer = self.statement_analyzer
        elif isinstance(node, Expression):
            analyzer = self.expression_analyzer

        analyze = getattr(analyzer, method_name, self.analyze_generic)

        node_type = analyze(node)

        if isinstance(node_type, CustomTypeIdentifier):
            template_symbol = self.symbol_table.lookup(node_type.name)
            if not template_symbol:
                raise NameError(f"Type {node_type.name} is not defined.")
            node_type = template_symbol.var_type

        return node_type

    def analyze_generic(self, node: Node) -> VarType:
        """Called if no explicit analyzer function exists for a node.
        Recursively analyses children.

        Args:
            node (Node): The AST node to analyse.

        Returns:
            VarType: The type of the node.
        """
        for attr_value in vars(node).values():
            if isinstance(attr_value, Node):
                self.analyze(attr_value)
            elif is_iterable(attr_value):
                for item in attr_value:
                    if isinstance(item, Node):
                        self.analyze(item)

        return PrimitiveType(TokenType.VOID)

    def analyze_program(self, node: Program) -> VoidType:
        """Starts semantic analysis from the root Program node.

        Args:
            node (Program): The Program node to analyse.

        Returns:
            VoidType: Void type.
        """
        self.symbol_table.enter_scope()
        for statement in node.body:
            self.analyze(statement)
        self.symbol_table.exit_scope()

        return VoidType()
