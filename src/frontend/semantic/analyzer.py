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
    """Analyzes the semantic meaning and validity of an AST."""

    def __init__(self) -> None:
        self.symbol_table = SymbolTable()
        self.statement_analyzer = StatementAnalyzer(self)
        self.expression_analyzer = ExpressionAnalyzer(self)

    def analyze(self, node: Node) -> VarType:
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

        node.type = node_type

        return node_type

    def analyze_generic(self, node: Node) -> VarType:
        for attr_value in vars(node).values():
            if isinstance(attr_value, Node):
                self.analyze(attr_value)
            elif is_iterable(attr_value):
                for item in attr_value:
                    if isinstance(item, Node):
                        self.analyze(item)

        return PrimitiveType(TokenType.VOID)

    def analyze_program(self, node: Program) -> VoidType:
        self.symbol_table.enter_scope()
        for statement in node.body:
            self.analyze(statement)
        self.symbol_table.exit_scope()

        return VoidType()
