from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from frontend.semantic.types import FunctionType, VarType, VoidType
from frontend.syntax.ast import *


class SymbolABC(ABC):
    """Abstract base class for symbol table entries."""

    name: str
    var_type: VarType


class ScopeABC(ABC):
    """Abstract base class for symbol table scopes."""

    symbols: Dict[str, SymbolABC]
    parent_node: Optional[Node]
    reachable: bool


class SymbolTableABC(ABC):
    """Abstract base class for symbol table."""

    scopes: List[ScopeABC]

    @abstractmethod
    def enter_scope(self, parent_node: Optional[Node] = None) -> None:
        """Enters a new scope and pushes it onto the scope stack.

        Args:
            parent_node (Optional[Statement]): The parent node of the scope.
        """

    @abstractmethod
    def exit_scope(self) -> None:
        """Exits the current scope and pops it from the scope stack.

        Raises:
            IndexError: If attempting to exit the global scope.
        """

    @abstractmethod
    def define(self, name: str, var_type: VarType) -> None:
        """Adds a symbol to the current scope.

        Args:
            name (str): The name of the symbol.
            var_type (VarType): The type of the symbol.

        Raises:
            KeyError: If the symbol is already declared in the current scope.
        """

    @abstractmethod
    def lookup(self, name: str, limit_to_function: bool = False) -> Optional[SymbolABC]:
        """Looks up a symbol by name, starting from the innermost scope.

        Args:
            name (str): The name of the symbol to lookup.
            limit_to_function (bool): Only search up to the nearest function scope.

        Returns:
            Optional[Symbol]: The symbol if found, otherwise `None`.
        """

    @abstractmethod
    def get_scope(self, symbol: SymbolABC) -> Optional[ScopeABC]:
        """Gets the scope containing the given symbol.

        Args:
            symbol (Symbol): The symbol to look up.

        Returns:
            Optional[Scope]: The scope containing the symbol if found, else `None`.
        """

    @abstractmethod
    def get_current_function_type(self) -> Optional[FunctionType]:
        """Gets the function type of the current function scope, if any.

        Returns:
            Optional[FunctionType]: The function type if in a function, else `None`.
        """

    @abstractmethod
    def is_loop_scope(self) -> bool:
        """Checks if the current scope is within a loop.

        Returns:
            bool: `True` if the current scope is within a loop, else `False`.
        """

    @abstractmethod
    def is_reachable(self) -> bool:
        """Checks if the current scope is reachable.

        Returns:
            bool: `True` if the current scope is reachable, else `False`.
        """

    @abstractmethod
    def set_unreachable(self) -> None:
        """Marks the current scope as unreachable."""


class ExpressionAnalyzerABC(ABC):
    """Abstract base class for the expression analyser."""

    @abstractmethod
    def analyze_binary_expression(self, node: BinaryExpression) -> VarType:
        """Analyses a BinaryExpression node.

        Args:
            node (BinaryExpression): The BinaryExpression node to analyse.

        Returns:
            VarType: The type of the binary expression.

        Raises:
            TypeError: If the operand types do not match the operator.
            TypeError: If the operator is invalid.
        """

    @abstractmethod
    def analyze_unary_expression(self, node: UnaryExpression) -> VarType:
        """Analyses a UnaryExpression node.

        Args:
            node (UnaryExpression): The UnaryExpression node to analyse.

        Returns:
            VarType: The type of the unary expression.

        Raises:
            TypeError: If the operand type does not match the operator.
            TypeError: If the operator is invalid.
        """

    @abstractmethod
    def analyze_assignment_expression(self, node: AssignmentExpression) -> VarType:
        """Analyses an AssignmentExpression node.

        Args:
            node (AssignmentExpression): The AssignmentExpression node to analyse.

        Returns:
            VarType: The type of the assignment expression.

        Raises:
            TypeError: If the variable type does not match the assigned value type.
            TypeError: If the assignment target is invalid.
        """

    @abstractmethod
    def analyze_identifier(self, node: Identifier) -> VarType:
        """Analyses an Identifier node.

        Args:
            node (Identifier): The Identifier node to analyse.

        Returns:
            VarType: The declared type of the identifier.

        Raises:
            NameError: If the identifier is not declared.
        """

    @abstractmethod
    def analyze_function_call_expression(self, node: FunctionCallExpression) -> VarType:
        """Analyses a FunctionCallExpression node.

        Args:
            node (FunctionCallExpression): The FunctionCallExpression node to analyse.

        Raises:
            NameError: If the function is not declared.
            TypeError: If the function is not a function type.
            TypeError: If the number of args does not match the function declaration.
            TypeError: If the argument types do not match the function declaration.

        Returns:
            VarType: The return type of the function.
        """

    @abstractmethod
    def analyze_index_expression(self, node: IndexExpression) -> VarType:
        """Analyses an IndexExpression node.

        Args:
            node (IndexExpression): The IndexExpression node to analyse.

        Returns:
            VarType: The type of the indexed value.

        Raises:
            TypeError: If the array index is not an integer.
            TypeError: If the array is not an array type.
        """

    @abstractmethod
    def analyze_member_access_expression(self, node: MemberAccessExpression) -> VarType:
        """Analyses a MemberAccessExpression node.

        Args:
            node (MemberAccessExpression): The MemberAccessExpression node to analyse.

        Returns:
            VarType: The type of the member.

        Raises:
            TypeError: If the compositeect type does not have the member.
        """

    @abstractmethod
    def analyze_method_call_expression(self, node: MethodCallExpression) -> VarType:
        """Analyses a MethodCallExpression node.

        Args:
            node (MethodCallExpression): The MethodCallExpression node to analyse.

        Returns:
            VarType: The return type of the method.

        Raises:
            TypeError: If the compositeect type does not have the method.
            TypeError: If the argument types do not match the method declaration.
        """

    # Literals
    @abstractmethod
    def analyze_numeric_literal(self, node: NumericLiteral) -> VarType:
        """Analyses a NumericLiteral node.

        Args:
            node (NumericLiteral): The NumericLiteral node to analyse.

        Returns:
            VarType: The type of the numeric literal.
        """

    @abstractmethod
    def analyze_string_literal(self, node: StringLiteral) -> VarType:
        """Analyses a StringLiteral node.

        Args:
            node (StringLiteral): The StringLiteral node to analyse.

        Returns:
            VarType: The type of the string literal.
        """

    @abstractmethod
    def analyze_boolean_literal(self, node: BooleanLiteral) -> VarType:
        """Analyses a BooleanLiteral node.

        Args:
            node (BooleanLiteral): The BooleanLiteral node to analyse.

        Returns:
            VarType: The type of the boolean literal.
        """

    @abstractmethod
    def analyze_null_literal(self, node: NullLiteral) -> VarType:
        """Analyses a NullLiteral node.

        Args:
            node (NullLiteral): The NullLiteral node to analyse.

        Returns:
            VarType: The type of the null literal.
        """

    @abstractmethod
    def analyze_array_literal(self, node: ArrayLiteral) -> VarType:
        """Analyses an ArrayLiteral node.

        Args:
            node (ArrayLiteral): The ArrayLiteral node to analyse.

        Returns:
            VarType: The type of the array.

        Raises:
            TypeError: If the element types are invalid.
        """

    @abstractmethod
    def analyze_set_literal(self, node: SetLiteral) -> VarType:
        """Analyses a SetLiteral node.

        Args:
            node (SetLiteral): The SetLiteral node to analyse.

        Returns:
            VarType: The type of the set.

        Raises:
            TypeError: If the element types are invalid.
        """

    @abstractmethod
    def analyze_map_literal(self, node: MapLiteral) -> VarType:
        """Analyses a MapLiteral node.

        Args:
            node (MapLiteral): The MapLiteral node to analyse.

        Returns:
            VarType: The type of the map.

        Raises:
            TypeError: If the key types are invalid.
            TypeError: If the value types are invalid.
        """

    @abstractmethod
    def analyze_entity_literal(self, node: EntityLiteral) -> VarType:
        """Analyses an EntityLiteral node.

        Args:
            node (EntityLiteral): The EntityLiteral node to analyse.

        Returns:
            VarType: The type of the entity.

        Raises:
            NameError: If the template is not declared.
            TypeError: If the attribute types do not match the template declaration.
        """

    @abstractmethod
    def analyze_function_literal(self, node: FunctionLiteral) -> VarType:
        """Analyses an FunctionLiteral node.

        Args:
            node (FunctionLiteral): The FunctionLiteral node to analyse.

        Returns:
            VarType: The type of the function literal.
        """


class StatementAnalyzerABC(ABC):
    """Abstract base class for the statement analyser."""

    @abstractmethod
    def analyze_variable_declaration(self, node: VariableDeclaration) -> VarType:
        """Analyses a VariableDeclaration node.

        Args:
            node (VariableDeclaration): The VariableDeclaration node to analyse.

        Returns:
            VarType: The type of the variable.

        Raises:
            NameError: If the variable has already been declared.
            NameError: If the variable shadows an existing variable.
            TypeError: If the variable type does not match the initializer type.
            TypeError: If the element type of a set is not hashable.
            TypeError: If the key type of a map is not hashable.
        """

    @abstractmethod
    def analyze_function_declaration(self, node: FunctionDeclaration) -> FunctionType:
        """Analyses a FunctionDeclaration node.

        Args:
            node (FunctionDeclaration): The FunctionDeclaration node to analyse.
            context (Optional[TemplateType]): The template context for the function.

        Returns:
            VarType: The return type of the function.

        Raises:
            NameError: If the function has already been declared.
        """

    @abstractmethod
    def analyze_template_declaration(self, node: TemplateDeclaration) -> VarType:
        """Analyses a TemplateDeclaration node.

        Args:
            node (TemplateDeclaration): The TemplateDeclaration node to analyse.

        Returns:
            VarType: The return type of the template.

        Raises:
            NameError: If the template has already been declared.
        """

    @abstractmethod
    def analyze_block_statement(
        self, node: BlockStatement, new_scope: bool = True
    ) -> VoidType:
        """Analyses a BlockStatement node.

        Args:
            node (BlockStatement): The BlockStatement node to analyse.
            new_scope (bool): Whether to create a new scope for the block.

        Returns:
            VoidType: Void type.

        Raises:
            SyntaxError: If unreachable code is detected.
        """

    @abstractmethod
    def analyze_if_statement(self, node: IfStatement) -> VoidType:
        """Analyses an IfStatement node.

        Args:
            node (IfStatement): The IfStatement node to analyse.

        Returns:
            VoidType: Void type.

        Raises:
            TypeError: If the condition is not a boolean.
            SyntaxError: If unreachable code is detected.
        """

    @abstractmethod
    def analyze_while_statement(self, node: WhileStatement) -> VoidType:
        """Analyses a WhileStatement node.

        Args:
            node (WhileStatement): The WhileStatement node to analyse.

        Returns:
            VarType: The type of the while statement.

        Raises:
            TypeError: If the condition is not a boolean.
        """

    @abstractmethod
    def analyze_range_statement(self, node: RangeStatement) -> VoidType:
        """Analyses a RangeStatement node.

        Args:
            node (RangeStatement): The RangeStatement node to analyse.

        Returns:
            VoidType: Void type.

        Raises:
            TypeError: If the range boundaries and increment are not integers.
        """

    @abstractmethod
    def analyze_each_statement(self, node: EachStatement) -> VoidType:
        """Analyses an EachStatement node.

        Args:
            node (EachStatement): The EachStatement node to analyse.

        Returns:
            VoidType: Void type.

        Raises:
            TypeError: If the iterable is not an array.
        """

    @abstractmethod
    def analyze_halt_statement(self, node: HaltStatement) -> VoidType:
        """Analyses a HaltStatement.

        Args:
            node (HaltStatement): The HaltStatement node to analyse.

        Returns:
            VoidType: Void type.

        Raises:
            SyntaxError: If the halt statement is not within a loop block.
        """

    @abstractmethod
    def analyze_skip_statement(self, node: SkipStatement) -> VoidType:
        """Analyses a SkipStatement.

        Args:
            node (SkipStatement): The SkipStatement node to analyse.

        Returns:
            VoidType: Void type.

        Raises:
            SyntaxError: If the skip statement is not within a loop block.
        """

    @abstractmethod
    def analyze_echo_statement(self, node: EchoStatement) -> VoidType:
        """Analyses an EchoStatement node.

        Args:
            node (EchoStatement): The EchoStatement node to analyse.

        Returns:
            VarType: The type of the echo statement.
        """

    @abstractmethod
    def analyze_return_statement(self, node: ReturnStatement) -> VarType:
        """Analyses a ReturnStatement node.

        Args:
            node (ReturnStatement): The ReturnStatement node to analyse.

        Returns:
            VarType: The return type of the function.
        """

    @abstractmethod
    def get_return_type(self, node: ReturnStatement) -> VarType:
        """Checks the return type of a ReturnStatement node.

        Args:
            node (ReturnStatement): The ReturnStatement node to check.

        Returns:
            VarType: The return type of the function.

        Raises:
            SyntaxError: If the return statement is not within a function block.
            TypeError: If the return type does not match the function return type.
        """


class SemanticAnalyzerABC(ABC):
    """Abstract base class for the semantic analyser."""

    symbol_table: SymbolTableABC
    statement_analyzer: StatementAnalyzerABC
    expression_analyzer: ExpressionAnalyzerABC

    @abstractmethod
    def analyze(self, node: Node) -> VarType:
        """Analyses a node in the AST.

        Args:
            node (Node): The AST node to analyse.

        Returns:
            VarType: The type of the node.

        Raises:
            SyntaxError: If unreachable code is detected.
        """

    @abstractmethod
    def analyze_generic(self, node: Node) -> VarType:
        """Called if no explicit analyser method exists for a node.

        Args:
            node (Node): The AST node to analyse.

        Returns:
            VarType: The type of the node.
        """

    @abstractmethod
    def analyze_program(self, node: Program) -> VoidType:
        """Starts semantic analysis from the root Program node.

        Args:
            node (Program): The Program node to analyse.

        Returns:
            VoidType: Void type.
        """
