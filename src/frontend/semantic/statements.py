from frontend.semantic.typing import SemanticAnalyzerABC, StatementAnalyzerABC
from frontend.semantic.types import (
    ArrayType,
    InferType,
    PrimitiveType,
    VarType,
    VoidType,
)
from frontend.syntax.ast import *


class StatementAnalyzer(StatementAnalyzerABC):
    """Class that provides methods for analyzing the semantic validity of statements."""

    def __init__(self, analyzer: SemanticAnalyzerABC) -> None:
        self.analyzer = analyzer

    def analyze_variable_declaration(self, node: VariableDeclaration) -> VarType:
        """Analyses a VariableDeclaration node, adding the variable to the symbol table and checking its type.

        Args:
            node (VariableDeclaration): The VariableDeclaration node to analyse.

        Returns:
            VarType: The type of the variable.

        Raises:
            NameError: If the variable is redeclared.
            NameError: If the variable shadows an existing variable.
            TypeError: If the variable type does not match the initializer type.
        """
        init_type = self.analyzer.analyze(node.initializer)

        existing_symbol = self.analyzer.symbol_table.lookup(node.name, True)

        if existing_symbol:
            existing_scope = self.analyzer.symbol_table.get_scope(existing_symbol)
            if existing_scope == self.analyzer.symbol_table.scopes[-1]:
                raise NameError(f'Cannot redeclare variable "{node.name}"')

            raise NameError(f'Cannot shadow existing variable "{node.name}"')

        if isinstance(node.var_type, InferType):
            node.var_type = init_type  # Infer the variable type from the initializer
        if node.var_type != init_type:
            raise TypeError(
                f"Type mismatch for variable {node.name}: {node.var_type} != {init_type}"
            )

        self.analyzer.symbol_table.define(node.name, node.var_type)

        return node.var_type

    def analyze_function_declaration(self, node: FunctionDeclaration) -> VarType:
        """Analyses a FunctionDeclaration node, adding the function to the symbol table and managing parameter scope.

        Args:
            node (FunctionDeclaration): The FunctionDeclaration node to analyse.

        Returns:
            VarType: The return type of the function.

        Raises:
            NameError: If the function is redeclared.
        """
        if self.analyzer.symbol_table.lookup(node.name, True):
            raise NameError(f'Cannot redeclare function "{node.name}"')

        self.analyzer.symbol_table.define(node.name, node.function_type)

        self.analyzer.symbol_table.enter_scope(node)
        for param_name, param_type in node.function_type.param_types:
            self.analyzer.symbol_table.define(param_name, param_type)
        self.analyze_block_statement(node.body, False)
        self.analyzer.symbol_table.exit_scope()

        return node.function_type.return_type

    def analyze_block_statement(
        self, node: BlockStatement, new_scope: bool = True
    ) -> VoidType:
        """Analyses a BlockStatement node, managing scope entering and exiting.

        Args:
            node (BlockStatement): The BlockStatement node to analyse.

        Returns:
            VoidType: Void type.

        Raises:
            SyntaxError: If unreachable code is detected.
        """
        if new_scope:
            self.analyzer.symbol_table.enter_scope()

        for statement in node.statements:
            if not self.analyzer.symbol_table.is_reachable():
                raise SyntaxError(f"Unreachable code detected at {statement}")
            self.analyzer.analyze(statement)

        if new_scope:
            self.analyzer.symbol_table.exit_scope()

        return VoidType()

    def analyze_if_statement(self, node: IfStatement) -> VoidType:
        """Analyses an IfStatement node, checking the condition and branches.

        Args:
            node (IfStatement): The IfStatement node to analyse.

        Returns:
            VoidType: Void type.

        Raises:
            TypeError: If the condition is not a boolean.
            SyntaxError: If unreachable code is detected.
        """
        if not self.analyzer.symbol_table.is_reachable():
            raise SyntaxError(f"Unreachable code detected at {node}")

        cond_type = self.analyzer.analyze(node.condition)
        if cond_type != PrimitiveType(TokenType.BOOL):
            raise TypeError("Condition of if statement must be a boolean")

        if isinstance(node.condition, BooleanLiteral) and node.condition.value is True:
            then_reachable = self._analyze_then_block(node)
            if node.else_block:
                raise SyntaxError("Unreachable else block detected")

        elif (
            isinstance(node.condition, BooleanLiteral) and node.condition.value is False
        ):
            if node.then_block.statements:
                raise SyntaxError("Unreachable if block detected")
            self._analyze_else_block(node)

        else:
            then_reachable = self._analyze_then_block(node)
            else_reachable = self._analyze_else_block(node)

            if not then_reachable and not else_reachable:
                self.analyzer.symbol_table.set_unreachable()

        return VoidType()

    def _analyze_then_block(self, node: IfStatement):
        self.analyzer.symbol_table.enter_scope(node)
        self.analyze_block_statement(node.then_block, False)
        then_reachable = self.analyzer.symbol_table.is_reachable()
        self.analyzer.symbol_table.exit_scope()

        return then_reachable

    def _analyze_else_block(self, node: IfStatement):
        if node.else_block:
            self.analyzer.symbol_table.enter_scope(node)
            self.analyze_block_statement(node.else_block, False)
            else_reachable = self.analyzer.symbol_table.is_reachable()
            self.analyzer.symbol_table.exit_scope()

            return else_reachable

        return True

    def analyze_while_statement(self, node: WhileStatement) -> VoidType:
        """Analyses a WhileStatement node, checking the condition and body.

        Args:
            node (WhileStatement): The WhileStatement node to analyse.

        Returns:
            VarType: The type of the while statement.

        Raises:
            TypeError: If the condition is not a boolean.
        """
        cond_type = self.analyzer.analyze(node.condition)
        if cond_type != PrimitiveType(TokenType.BOOL):
            raise TypeError("Condition of while statement must be a boolean")

        self.analyzer.symbol_table.enter_scope(node)
        self.analyze_block_statement(node.body, False)
        self.analyzer.symbol_table.exit_scope()

        return VoidType()

    def analyze_range_statement(self, node: RangeStatement) -> VoidType:
        """Analyses a RangeStatement node, adding the variable to the symbol table and checking types.

        Args:
            node (RangeStatement): The RangeStatement node to analyse.

        Returns:
            VoidType: Void type.

        Raises:
            TypeError: If the range boundaries and increment are not integers.
        """
        start_type = self.analyzer.analyze(node.start)
        end_type = self.analyzer.analyze(node.end)
        increment_type = self.analyzer.analyze(node.increment)

        if (
            start_type != PrimitiveType(TokenType.INT)
            or end_type != PrimitiveType(TokenType.INT)
            or increment_type != PrimitiveType(TokenType.INT)
        ):
            raise TypeError("Range boundaries and increment must be integers")

        self.analyzer.symbol_table.enter_scope(node)
        self.analyzer.symbol_table.define(node.identifier, PrimitiveType(TokenType.INT))
        self.analyze_block_statement(node.body, False)
        self.analyzer.symbol_table.exit_scope()

        return VoidType()

    def analyze_each_statement(self, node: EachStatement) -> VoidType:
        """Analyses an EachStatement node, adding the iteration variable to the symbol table
        and creating a new scope for its body.

        Args:
            node (EachStatement): The EachStatement node to analyse.

        Returns:
            VoidType: Void type.

        Raises:
            TypeError: If the iterable is not an array.
        """
        iterable_type = self.analyzer.analyze(node.iterable)
        if not isinstance(iterable_type, ArrayType):
            raise TypeError("Each statement requires an array type for iteration")
        element_type = iterable_type.element_type

        self.analyzer.symbol_table.enter_scope(node)
        self.analyzer.symbol_table.define(node.variable, element_type)
        self.analyze_block_statement(node.body, False)
        self.analyzer.symbol_table.exit_scope()

        return VoidType()

    def analyze_halt_statement(self, node: HaltStatement) -> VoidType:
        """Analyses a HaltStatement node, marking the current scope as unreachable.

        Args:
            node (HaltStatement): The HaltStatement node to analyse.

        Returns:
            VoidType: Void type.

        Raises:
            SyntaxError: If the halt statement is not within a loop block.
        """
        if not self.analyzer.symbol_table.is_loop_scope():
            raise SyntaxError("Halt statement is not valid outside of a loop block")
        self.analyzer.symbol_table.set_unreachable()

        return VoidType()

    def analyze_skip_statement(self, node: SkipStatement) -> VoidType:
        if not self.analyzer.symbol_table.is_loop_scope():
            raise SyntaxError("Skip statement is not valid outside of a loop block")
        self.analyzer.symbol_table.set_unreachable()

        return VoidType()

    def analyze_echo_statement(self, node: EchoStatement) -> VoidType:
        """Analyses an EchoStatement node, checking the expression type.

        Args:
            node (EchoStatement): The EchoStatement node to analyse.

        Returns:
            VarType: The type of the echo statement.
        """
        self.analyzer.analyze(node.expression)

        return VoidType()

    def analyze_return_statement(self, node: ReturnStatement) -> VarType:
        """Analyses a ReturnStatement node, checking the return type.

        Args:
            node (ReturnStatement): The ReturnStatement node to analyse.

        Raises:
            SyntaxError: If the return statement is not within a function block.
            TypeError: If the return type does not match the function return type.

        Returns:
            VarType: The return type of the function.
        """
        fn_type = self.analyzer.symbol_table.get_current_function_type()
        if not fn_type:
            raise SyntaxError(
                "Return statement is not valid outside of a function block"
            )

        return_type = VoidType()
        if node.expression:
            return_type = self.analyzer.analyze(node.expression)
        if return_type != fn_type.return_type:
            raise TypeError(
                f"Return type {return_type} does not match function return type {fn_type.return_type}"
            )

        self.analyzer.symbol_table.set_unreachable()

        return return_type
