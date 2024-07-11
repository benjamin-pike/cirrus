from frontend.semantic.typing import SemanticAnalyzerABC, StatementAnalyzerABC
from frontend.semantic.types import *
from frontend.syntax.ast import *


class StatementAnalyzer(StatementAnalyzerABC):
    """Class that provides methods for analyzing the semantic validity of statements."""

    def __init__(self, analyzer: SemanticAnalyzerABC) -> None:
        self.analyzer = analyzer

    def analyze_variable_declaration(self, node: VariableDeclaration) -> VarType:
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
                f"Type mismatch for variable `{node.name}`: "
                f"`{node.var_type}` != `{init_type}`"
            )

        if isinstance(node.initializer, ArrayLiteral):
            assert isinstance(node.var_type, ArrayType)
            node.var_type.size = len(node.initializer.elements)
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
        if node.name == "_main":
            raise NameError("Cannot declare function with reserved name `_main`")
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
        if self.analyzer.symbol_table.lookup(node.name, False):
            raise NameError(f"Cannot redeclare template `{node.name}`")

        template_type = TemplateType(
            CustomTypeIdentifier(node.name), node.attributes, {}
        )
        for name, declaration in node.methods.items():
            template_type.methods[name] = self.analyze_function_declaration(
                declaration, template_type
            )

        self.analyzer.symbol_table.define(node.name, template_type)

        return template_type

    def analyze_block_statement(
        self, node: BlockStatement, new_scope: bool = True
    ) -> VoidType:
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

    def analyze_while_statement(self, node: WhileStatement) -> VoidType:
        cond_type = self.analyzer.analyze(node.condition)
        if cond_type != PrimitiveType(TokenType.BOOL):
            raise TypeError("Condition of while statement must be a boolean")

        self.analyzer.symbol_table.enter_scope(node)
        self.analyze_block_statement(node.body, False)
        self.analyzer.symbol_table.exit_scope()

        return VoidType()

    def analyze_range_statement(self, node: RangeStatement) -> VoidType:
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
        self.analyzer.analyze(node.expression)

        return VoidType()

    def analyze_return_statement(self, node: ReturnStatement) -> VarType:
        return_type = self.get_return_type(node)
        self.analyzer.symbol_table.set_unreachable()

        return return_type

    def get_return_type(self, node: ReturnStatement) -> VarType:
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

    def _analyze_then_block(self, node: IfStatement) -> bool:
        self.analyzer.symbol_table.enter_scope(node)
        self.analyze_block_statement(node.then_block, False)
        then_reachable = self.analyzer.symbol_table.is_reachable()
        self.analyzer.symbol_table.exit_scope()

        return then_reachable

    def _analyze_else_block(self, node: IfStatement) -> bool:
        if node.else_block:
            self.analyzer.symbol_table.enter_scope(node)
            self.analyze_block_statement(node.else_block, False)
            else_reachable = self.analyzer.symbol_table.is_reachable()
            self.analyzer.symbol_table.exit_scope()

            return else_reachable

        return True

    def _is_hashable_type(self, var_type: VarType) -> bool:
        """Checks if a variable type is hashable.

        Args:
            var_type (VarType): The variable type to check.

        Returns:
            bool: True if the variable type is hashable, otherwise False.
        """
        return isinstance(var_type, (PrimitiveType, SetType))
