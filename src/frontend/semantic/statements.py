from frontend.semantic.typing import SemanticAnalyzerABC, StatementAnalyzerABC
from frontend.semantic.types import *
from frontend.syntax.ast import *


class StatementAnalyzer(StatementAnalyzerABC):
    """Class that provides methods for analyzing the semantic validity of statements."""

    def __init__(self, analyzer: SemanticAnalyzerABC) -> None:
        self.analyzer = analyzer

    def analyze_variable_declaration(self, node: VariableDeclaration) -> VarType:
        """Analyses a VariableDeclaration node,
        adding the variable to the symbol table and checking its type.

        Args:
            node (VariableDeclaration): The VariableDeclaration node to analyse.

        Returns:
            VarType: The type of the variable.

        Raises:
            NameError: If the variable is redeclared.
            NameError: If the variable shadows an existing variable.
            TypeError: If the variable type does not match the initializer type.
            TypeError: If the element type of a set is not hashable.
            TypeError: If the key type of a map is not hashable.
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
        if isinstance(node.var_type, CustomType):
            template_symbol = self.analyzer.symbol_table.lookup(
                node.var_type.name, False
            )
            if not template_symbol:
                raise NameError(f"Template `{node.var_type.name}` not found")
            node.var_type = template_symbol.var_type
        if node.var_type != init_type:
            raise TypeError(
                f"Type mismatch for variable `{node.name}`: "
                f"`{node.var_type}` != `{init_type}`"
            )

        if isinstance(node.var_type, SetType):
            if not self._is_hashable_type(node.var_type.element_type):
                raise TypeError("Element type of set must be hashable")
        if isinstance(node.var_type, MapType):
            if not self._is_hashable_type(node.var_type.key_type):
                raise TypeError("Key type of map must be hashable")

        self.analyzer.symbol_table.define(node.name, node.var_type)

        return node.var_type

    def analyze_function_declaration(
        self, node: FunctionDeclaration, context: Optional[TemplateType] = None
    ) -> FunctionType:
        """Analyses a FunctionDeclaration node, adding the function
        to the symbol table and managing parameter scope.

        Args:
            node (FunctionDeclaration): The FunctionDeclaration node to analyse.
            context (Optional[TemplateType]): The template context for the function.

        Returns:
            VarType: The return type of the function.

        Raises:
            NameError: If the function is redeclared.
        """
        if self.analyzer.symbol_table.lookup(node.name, True):
            raise NameError(f'Cannot redeclare function "{node.name}"')

        self.analyzer.symbol_table.define(node.name, node.function_type)

        self.analyzer.symbol_table.enter_scope(node)
        if context:
            for attr_name, attr_type in context.attributes.items():
                self.analyzer.symbol_table.define(attr_name, attr_type)
            for method_name, method_type in context.methods.items():
                self.analyzer.symbol_table.define(method_name, method_type)
        for param_name, param_type in node.function_type.param_types:
            self.analyzer.symbol_table.define(param_name, param_type)

        self.analyze_block_statement(node.body, False)
        self.analyzer.symbol_table.exit_scope()

        return node.function_type

    def analyze_template_declaration(self, node: TemplateDeclaration) -> VarType:
        """Analyses a TemplateDeclaration node, adding the template
        to the symbol table and managing parameter scope.

        Args:
            node (TemplateDeclaration): The TemplateDeclaration node to analyse.

        Returns:
            VarType: The return type of the template.

        Raises:
            NameError: If the template is redeclared.
        """
        if self.analyzer.symbol_table.lookup(node.name, False):
            raise NameError(f"Cannot redeclare template `{node.name}`")

        template_type = TemplateType(CustomType(node.name), node.attributes, {})
        for name, declaration in node.methods.items():
            template_type.methods[name] = self.analyze_function_declaration(
                declaration, template_type
            )

        self.analyzer.symbol_table.define(node.name, template_type)

        return template_type

    def analyze_block_statement(
        self, node: BlockStatement, new_scope: bool = True
    ) -> VoidType:
        """Analyses a BlockStatement node, managing scope entering and exiting.

        Args:
            node (BlockStatement): The BlockStatement node to analyse.
            new_scope (bool): Whether to create a new scope for the block.

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

    def _analyze_then_block(self, node: IfStatement) -> bool:
        """Analyzes the then block of an IfStatement node.

        Args:
            node (IfStatement): The IfStatement node to analyse.

        Returns:
            bool: True if the then block is reachable, otherwise False.
        """
        self.analyzer.symbol_table.enter_scope(node)
        self.analyze_block_statement(node.then_block, False)
        then_reachable = self.analyzer.symbol_table.is_reachable()
        self.analyzer.symbol_table.exit_scope()

        return then_reachable

    def _analyze_else_block(self, node: IfStatement) -> bool:
        """Analyzes the else block of an IfStatement node.

        Args:
            node (IfStatement): The IfStatement node to analyse.

        Returns:
            bool: True if the else block is reachable, otherwise False.
        """
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
        """Analyses a RangeStatement node, adding the
        variable to the symbol table and checking types.

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
        """Analyses an EachStatement node, adding the iteration variable
        to the symbol table and creating a new scope for its body.

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
        """Analyses a HaltStatement, marking the current scope as unreachable.

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
        """Analyses a SkipStatement, marking the current scope as unreachable.

        Args:
            node (SkipStatement): The SkipStatement node to analyse.

        Returns:
            VoidType: Void type.

        Raises:
            SyntaxError: If the skip statement is not within a loop block.
        """
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

        Returns:
            VarType: The return type of the function.
        """
        return_type = self.get_return_type(node)
        self.analyzer.symbol_table.set_unreachable()

        return return_type

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
        fn_type = self.analyzer.symbol_table.get_current_function_type()
        if not fn_type:
            raise SyntaxError(
                "Return statement is not valid outside of a function block"
            )

        return_type = VoidType()
        if node.expression:
            return_type = self.analyzer.analyze(node.expression)

        if fn_type.return_type == InferType():
            fn_type.return_type = return_type
        elif return_type != fn_type.return_type:
            raise TypeError(
                f"Return type `{return_type}` does not match "
                f"function return type `{fn_type.return_type}`"
            )

        return return_type

    def _is_hashable_type(self, var_type: VarType) -> bool:
        """Checks if a variable type is hashable.

        Args:
            var_type (VarType): The variable type to check.

        Returns:
            bool: True if the variable type is hashable, otherwise False.
        """
        return isinstance(var_type, (PrimitiveType, SetType))
