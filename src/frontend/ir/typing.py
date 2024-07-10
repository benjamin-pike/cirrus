from abc import ABC, abstractmethod
from llvmlite import ir, binding as llvm
from frontend.syntax.ast import *


class ExpressionGeneratorABC(ABC):
    """Abstract base class for expression generators"""

    @abstractmethod
    def generate_numeric_literal(self, node: NumericLiteral) -> ir.Value:
        """Generate LLVM IR for a numeric literal."""

    @abstractmethod
    def generate_string_literal(self, node: StringLiteral) -> ir.Value:
        """Generate LLVM IR for a string literal."""

    @abstractmethod
    def generate_boolean_literal(self, node: BooleanLiteral) -> ir.Value:
        """Generate LLVM IR for a boolean literal."""

    @abstractmethod
    def generate_array_literal(self, node: ArrayLiteral) -> ir.Value:
        """Generate LLVM IR for an array literal."""

    @abstractmethod
    def generate_identifier(self, node: Identifier) -> ir.Value:
        """Generate LLVM IR for an identifier."""

    @abstractmethod
    def generate_unary_expression(self, node: UnaryExpression) -> ir.Value:
        """Generate LLVM IR for a unary expression."""

    @abstractmethod
    def generate_binary_expression(self, node: BinaryExpression) -> ir.Value:
        """Generate LLVM IR for a binary expression."""

    @abstractmethod
    def generate_assignment_expression(self, node: AssignmentExpression) -> ir.Value:
        """Generate LLVM IR for an assignment expression."""

    @abstractmethod
    def generate_index_expression(self, node: IndexExpression) -> ir.Value:
        """Generate LLVM IR for an index expression."""

    @abstractmethod
    def generate_function_call_expression(
        self, node: FunctionCallExpression
    ) -> ir.Value:
        """Generate LLVM IR for a function call expression."""


class StatementGeneratorABC(ABC):
    """Abstract base class for statement generators"""

    @abstractmethod
    def generate_variable_declaration(self, node: VariableDeclaration) -> None:
        """Generate LLVM IR for a variable declaration."""

    @abstractmethod
    def generate_function_declaration(self, node: FunctionDeclaration) -> None:
        """Generate LLVM IR for a function declaration."""

    @abstractmethod
    def generate_return_statement(self, node: ReturnStatement) -> None:
        """Generate LLVM IR for a return statement."""

    @abstractmethod
    def generate_block_statement(self, node: BlockStatement) -> None:
        """Generate LLVM IR for a block statement."""

    @abstractmethod
    def generate_if_statement(self, node: IfStatement) -> None:
        """Generate LLVM IR for an if statement."""

    @abstractmethod
    def generate_while_statement(self, node: WhileStatement) -> None:
        """Generate LLVM IR for a while statement."""

    @abstractmethod
    def generate_each_statement(self, node: EachStatement) -> None:
        """Generate LLVM IR for an each statement."""

    @abstractmethod
    def generate_range_statement(self, node: RangeStatement) -> None:
        """Generate LLVM IR for a range statement."""

    @abstractmethod
    def generate_expression_statement(self, node: ExpressionStatement) -> None:
        """Generate LLVM IR for an expression statement."""

    @abstractmethod
    def generate_echo_statement(self, node: EchoStatement) -> None:
        """Generate LLVM IR for an echo statement."""


class IRGeneratorABC(ABC):
    """Abstract base class for IR generators"""

    module: ir.Module
    builder: ir.IRBuilder
    func: ir.Function
    block: ir.Block

    target_data: llvm.TargetData

    statement_generator: StatementGeneratorABC
    expression_generator: ExpressionGeneratorABC

    symbol_table: dict[str, ir.Value]

    @abstractmethod
    def generate_program(self, node: Program) -> ir.Module:
        """Generate LLVM IR from a program node."""

    @abstractmethod
    def generate_statement(self, node: Statement) -> ir.Module:
        """Generate LLVM IR from a statement node."""

    @abstractmethod
    def generate_expression(self, node: Expression) -> ir.Value:
        """Generate LLVM IR from an expression node."""
