from semantic.types import VarType, VoidType
from syntax.ast import *

class SymbolABC(Protocol):
    name: str
    var_type: VarType

class ScopeABC(Protocol):
    symbols: Dict[str, SymbolABC]
    parent_node: Optional[Statement]
    reachable: bool

class SymbolTableABC(Protocol):
    scopes: List[ScopeABC]

    def __init__(self) -> None: ...
    def enter_scope(self, parent_node: Optional[Statement] = None) -> None: ...
    def exit_scope(self) -> None: ...
    def define(self, name: str, var_type: VarType) -> None: ...
    def lookup(self, name: str, limit_to_function: bool = False) -> Optional[SymbolABC]: ...
    def get_scope(self, symbol: SymbolABC) -> Optional[ScopeABC]: ...
    def get_current_function_type(self) -> Optional[FunctionType]: ...
    def is_loop_scope(self) -> bool: ...
    def is_reachable(self) -> bool: ...
    def set_unreachable(self) -> None: ...

class SemanticAnalyzerABC(Protocol):
    symbol_table: SymbolTableABC

    def analyze(self, node: Node) -> VarType: ...
    def analyze_generic(self, node: Node) -> VarType: ...
    def analyze_program(self, node: Program) -> VoidType: ...

class StatementAnalyzerABC(Protocol):
    def analyze_variable_declaration(self, node: VariableDeclaration) -> VarType: ...
    def analyze_function_declaration(self, node: FunctionDeclaration) -> VarType: ...
    def analyze_block_statement(self, node: BlockStatement, new_scope: bool = True) -> VoidType: ...
    def analyze_if_statement(self, node: IfStatement) -> VoidType: ...
    def analyze_while_statement(self, node: WhileStatement) -> VoidType: ...
    def analyze_range_statement(self, node: RangeStatement) -> VoidType: ...
    def analyze_each_statement(self, node: EachStatement) -> VoidType: ...
    def analyze_halt_statement(self, node: HaltStatement) -> VoidType: ...
    def analyze_skip_statement(self, node: SkipStatement) -> VoidType: ...
    def analyze_echo_statement(self, node: EchoStatement) -> VoidType: ...
    def analyze_return_statement(self, node: ReturnStatement) -> VarType: ...

class ExpressionAnalyzerABC(Protocol):
    def analyze_binary_expression(self, node: BinaryExpression) -> VarType: ...
    def analyze_unary_expression(self, node: UnaryExpression) -> VarType: ...
    def analyze_assignment_expression(self, node: AssignmentExpression) -> VarType: ...
    def analyze_numeric_literal(self, node: NumericLiteral) -> VarType: ...
    def analyze_string_literal(self, node: StringLiteral) -> VarType: ...
    def analyze_boolean_literal(self, node: BooleanLiteral) -> VarType: ...
    def analyze_null_literal(self, node: NullLiteral) -> VarType: ...
    def analyze_identifier(self, node: Identifier) -> VarType: ...
    def analyze_call_expression(self, node: CallExpression) -> VarType: ...
    def analyze_array_literal(self, node: ArrayLiteral) -> VarType: ...
    def analyze_index_expression(self, node: IndexExpression) -> VarType: ...
    def _is_assignable(self, node: Expression) -> bool: ...