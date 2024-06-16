from typing import Dict, List, Optional, Protocol
from abc import ABC, abstractmethod
from frontend.semantic.types import FunctionType, VarType, VoidType
from frontend.syntax.ast import *


class SymbolABC(Protocol):
    """Abstract class for symbol table entries."""

    name: str
    var_type: VarType


class ScopeABC(Protocol):
    """Abstract class for symbol table scopes."""

    symbols: Dict[str, SymbolABC]
    parent_node: Optional[Statement]
    reachable: bool


class SymbolTableABC(ABC):
    """Abstract class for symbol table."""

    scopes: List[ScopeABC]

    @abstractmethod
    def enter_scope(self, parent_node: Optional[Statement] = None) -> None:
        """Push a new scope onto the stack."""

    @abstractmethod
    def exit_scope(self) -> None:
        """Pop the current scope from the stack."""

    @abstractmethod
    def define(self, name: str, var_type: VarType) -> None:
        """Define a new symbol in the current scope."""

    @abstractmethod
    def lookup(self, name: str, limit_to_function: bool = False) -> Optional[SymbolABC]:
        """Lookup a symbol in the current scope and all parent scopes."""

    @abstractmethod
    def get_scope(self, symbol: SymbolABC) -> Optional[ScopeABC]:
        """Get the scope that contains the given symbol."""

    @abstractmethod
    def get_current_function_type(self) -> Optional[FunctionType]:
        """Get the type of the current function scope."""

    @abstractmethod
    def is_loop_scope(self) -> bool:
        """Check if the current scope is a loop scope."""

    @abstractmethod
    def is_reachable(self) -> bool:
        """Check if the current scope is reachable."""

    @abstractmethod
    def set_unreachable(self) -> None:
        """Set the current scope to unreachable."""


class SemanticAnalyzerABC(ABC):
    """Abstract class for the semantic analyzer."""

    symbol_table: SymbolTableABC

    @abstractmethod
    def analyze(self, node: Node) -> VarType:
        """Analyze a node in the AST."""

    @abstractmethod
    def analyze_generic(self, node: Node) -> VarType:
        """Analyze a node of an unknown type."""

    @abstractmethod
    def analyze_program(self, node: Program) -> VoidType:
        """Analyze a program node."""


class StatementAnalyzerABC(ABC):
    """Abstract class for the statement analyzer."""

    @abstractmethod
    def analyze_variable_declaration(self, node: VariableDeclaration) -> VarType:
        """Analyze a variable declaration statement."""

    @abstractmethod
    def analyze_function_declaration(self, node: FunctionDeclaration) -> VarType:
        """Analyze a function declaration statement."""

    @abstractmethod
    def analyze_block_statement(
        self, node: BlockStatement, new_scope: bool = True
    ) -> VoidType:
        """Analyze a block statement."""

    @abstractmethod
    def analyze_if_statement(self, node: IfStatement) -> VoidType:
        """Analyze an if statement."""

    @abstractmethod
    def analyze_while_statement(self, node: WhileStatement) -> VoidType:
        """Analyze a while statement."""

    @abstractmethod
    def analyze_range_statement(self, node: RangeStatement) -> VoidType:
        """Analyze a range statement."""

    @abstractmethod
    def analyze_each_statement(self, node: EachStatement) -> VoidType:
        """Analyze an each statement."""

    @abstractmethod
    def analyze_halt_statement(self, node: HaltStatement) -> VoidType:
        """Analyze a halt statement."""

    @abstractmethod
    def analyze_skip_statement(self, node: SkipStatement) -> VoidType:
        """Analyze a skip statement."""

    @abstractmethod
    def analyze_echo_statement(self, node: EchoStatement) -> VoidType:
        """Analyze an echo statement."""

    @abstractmethod
    def analyze_return_statement(self, node: ReturnStatement) -> VarType:
        """Analyze a return statement."""


class ExpressionAnalyzerABC(ABC):
    """Abstract class for the expression analyzer."""

    @abstractmethod
    def analyze_binary_expression(self, node: BinaryExpression) -> VarType:
        """Analyze a binary expression."""

    @abstractmethod
    def analyze_unary_expression(self, node: UnaryExpression) -> VarType:
        """Analyze a unary expression."""

    @abstractmethod
    def analyze_assignment_expression(self, node: AssignmentExpression) -> VarType:
        """Analyze an assignment expression."""

    @abstractmethod
    def analyze_numeric_literal(self, node: NumericLiteral) -> VarType:
        """Analyze a numeric literal."""

    @abstractmethod
    def analyze_string_literal(self, node: StringLiteral) -> VarType:
        """Analyze a string literal."""

    @abstractmethod
    def analyze_boolean_literal(self, node: BooleanLiteral) -> VarType:
        """Analyze a boolean literal."""

    @abstractmethod
    def analyze_null_literal(self, node: NullLiteral) -> VarType:
        """Analyze a null literal."""

    @abstractmethod
    def analyze_identifier(self, node: Identifier) -> VarType:
        """Analyze an identifier."""

    @abstractmethod
    def analyze_call_expression(self, node: CallExpression) -> VarType:
        """Analyze a call expression."""

    @abstractmethod
    def analyze_array_literal(self, node: ArrayLiteral) -> VarType:
        """Analyze an array literal."""

    @abstractmethod
    def analyze_index_expression(self, node: IndexExpression) -> VarType:
        """Analyze an index expression."""

    @abstractmethod
    def _is_assignable(self, node: Expression) -> bool:
        """Check if an expression is assignable."""
