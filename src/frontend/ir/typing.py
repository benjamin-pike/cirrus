from abc import ABC, abstractmethod
from llvmlite import ir, binding as llvm
from frontend.syntax.ast import *


# Expressions
class ArrayGeneratorABC(ABC):
    """Abstract base class for array generators"""

    @abstractmethod
    def generate_array_literal(self, node: ArrayLiteral) -> ir.Value:
        """Generate LLVM IR for an array literal.

        Args:
            node (ArrayLiteral): The array literal node

        Returns:
            ir.Value: The LLVM IR value (pointer to array struct)
        """

    @abstractmethod
    def generate_index_expression(self, node: IndexExpression) -> ir.Value:
        """Generate LLVM IR for an index expression.

        Args:
            node (IndexExpression): The index expression node

        Returns:
            ir.Value: The LLVM IR value of the indexed element
        """

    @abstractmethod
    def generate_array_method_call(self, node: MethodCallExpression) -> ir.Value:
        """Generate LLVM IR for an array method call.

        Args:
            node (MethodCallExpression): The method call expression node

        Returns:
            ir.Value: The LLVM IR value of the method call result
        """


class StringGeneratorABC(ABC):
    """Abstract base class for string generators"""

    @abstractmethod
    def generate_string_literal(self, node: StringLiteral) -> ir.Value:
        """Generate LLVM IR for a string literal.

        Args:
            node (StringLiteral): The string literal node

        Returns:
            ir.Value: The bitcasted global variable pointer to the string literal
        """

    @abstractmethod
    def compare_strings(
        self, left: ir.Value, right: ir.Value, cmp_op: str
    ) -> ir.Instruction:
        """Generate LLVM IR to compare two strings.

        Args:
            left (ir.Value): The left string to compare
            right (ir.Value): The right string to compare
            cmp_op (str): The comparison operator

        Returns:
            ir.Instruction: The comparison instruction
        """

    @abstractmethod
    def concat_strings(self, left: ir.Value, right: ir.Value) -> ir.Value:
        """Generate LLVM IR to concatenate two strings.

        Args:
            left (ir.Value): The left string to concatenate
            right (ir.Value): The right string to concatenate

        Returns:
            ir.Value: The pointer to the concatenated string
        """


class ExpressionGeneratorABC(ABC):
    """Abstract base class for expression generators"""

    @abstractmethod
    def generate_numeric_literal(self, node: NumericLiteral) -> ir.Value:
        """Generate LLVM IR for a numeric literal.

        Args:
            node (NumericLiteral): The numeric literal node

        Returns:
            ir.Value: The LLVM IR value, int or float (constant)
        """

    @abstractmethod
    def generate_boolean_literal(self, node: BooleanLiteral) -> ir.Value:
        """Generate LLVM IR for a boolean literal.

        Args:
            node (BooleanLiteral): The boolean literal node

        Returns:
            ir.Value: The LLVM IR bool value (constant)
        """

    @abstractmethod
    def generate_string_literal(self, node: StringLiteral) -> ir.Value:
        """Generate LLVM IR for a string literal.

        Args:
            node (StringLiteral): The string literal node

        Returns:
            ir.Value: The bitcasted global variable pointer to the string literal
        """

    @abstractmethod
    def generate_null_literal(self, _node: NullLiteral) -> ir.Value:
        """Generate LLVM IR for a null literal.

        Args:
            _node (NullLiteral): The null literal node

        Returns:
            ir.Value: The LLVM null pointer value (constant)
        """

    @abstractmethod
    def generate_identifier(self, node: Identifier) -> ir.Value:
        """Generate LLVM IR for an identifier.

        Args:
            node (Identifier): The identifier node

        Returns:
            ir.Value: The LLVM IR value (variable or function)
        """

    @abstractmethod
    def generate_unary_expression(self, node: UnaryExpression) -> ir.Value:
        """Generate LLVM IR for a unary expression.

        Args:
            node (UnaryExpression): The unary expression node

        Returns:
            ir.Value: The LLVM IR value resulting from the unary operation
        """

    @abstractmethod
    def generate_binary_expression(self, node: BinaryExpression) -> ir.Value:
        """Generate LLVM IR for a binary expression.

        Args:
            node (BinaryExpression): The binary expression node

        Returns:
            ir.Value: The LLVM IR value resulting from the binary operation
        """

    @abstractmethod
    def generate_assignment_expression(self, node: AssignmentExpression) -> ir.Value:
        """Generate LLVM IR for an assignment expression.

        Args:
            node (AssignmentExpression): The assignment expression node

        Returns:
            ir.Value: The LLVM IR value of the assigned expression
        """

    @abstractmethod
    def generate_function_call_expression(
        self, node: FunctionCallExpression
    ) -> ir.Value:
        """Generate LLVM IR for a function call expression.

        Args:
            node (FunctionCallExpression): The function call expression node

        Returns:
            ir.Value: The LLVM IR value of the function call result
        """

    @abstractmethod
    def generate_method_call_expression(self, node: MethodCallExpression) -> ir.Value:
        """Generate LLVM IR for a method call expression.

        Args:
            node (MethodCallExpression): The method call expression node

        Returns:
            ir.Value: The LLVM IR value of the method call result
        """


# Statements
class LoopGeneratorABC(ABC):
    """Abstract base class for loop generators"""

    @abstractmethod
    def generate_while_statement(self, node: WhileStatement) -> None:
        """Generate LLVM IR for a while statement.

        Args:
            node (WhileStatement): The while statement node
        """

    @abstractmethod
    def generate_each_statement(self, node: EachStatement) -> None:
        """Generate LLVM IR for an each statement.

        Args:
            node (EachStatement): The each statement node
        """

    @abstractmethod
    def generate_range_statement(self, node: RangeStatement) -> None:
        """Generate LLVM IR for a range statement.

        Args:
            node (RangeStatement): The range statement node
        """

    @abstractmethod
    def generate_halt_statement(self, _node: HaltStatement) -> None:
        """Generate LLVM IR for a halt statement.

        Args:
            _node (HaltStatement): The halt statement node
        """

    @abstractmethod
    def generate_skip_statement(self, _node: SkipStatement) -> None:
        """Generate LLVM IR for a skip statement.

        Args:
            _node (SkipStatement): The skip statement node
        """


class StatementGeneratorABC(ABC):
    """Abstract base class for statement generators"""

    @abstractmethod
    def generate_expression_statement(self, node: ExpressionStatement) -> None:
        """Generate LLVM IR for an expression statement.

        Args:
            node (ExpressionStatement): The expression statement node
        """

    @abstractmethod
    def generate_variable_declaration(self, node: VariableDeclaration) -> None:
        """Generate LLVM IR for a variable declaration.

        Args:
            node (VariableDeclaration): The variable declaration node
        """

    @abstractmethod
    def generate_function_declaration(self, node: FunctionDeclaration) -> None:
        """Generate LLVM IR for a function declaration.

        Args:
            node (FunctionDeclaration): The function declaration node
        """

    @abstractmethod
    def generate_return_statement(self, node: ReturnStatement) -> None:
        """Generate LLVM IR for a return statement.

        Args:
            node (ReturnStatement): The return statement node
        """

    @abstractmethod
    def generate_block_statement(self, node: BlockStatement) -> None:
        """Generate LLVM IR for a block statement.

        Args:
            node (BlockStatement): The block statement node
        """

    @abstractmethod
    def generate_if_statement(self, node: IfStatement) -> None:
        """Generate LLVM IR for an if statement.

        Args:
            node (IfStatement): The if statement node
        """

    @abstractmethod
    def generate_echo_statement(self, node: EchoStatement) -> None:
        """Generate LLVM IR for an echo statement.

        Args:
            node (EchoStatement): The echo statement node
        """


# Program
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
