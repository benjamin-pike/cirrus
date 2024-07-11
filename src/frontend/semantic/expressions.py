from frontend.semantic.types import *
from frontend.semantic.types import VarType
from frontend.semantic.typing import *
from frontend.syntax.ast import *


class ExpressionAnalyzer(ExpressionAnalyzerABC):
    """Class that provides methods for analysing the expression semantics."""

    def __init__(self, analyzer: SemanticAnalyzerABC) -> None:
        self.analyzer = analyzer

    def analyze_binary_expression(self, node: BinaryExpression) -> VarType:
        left_type = self.analyzer.analyze(node.left)
        right_type = self.analyzer.analyze(node.right)

        if left_type != right_type:
            raise TypeError(
                f"Type mismatch in binary expression: {left_type} != {right_type}"
            )

        match node.operator:
            # Arithmetic operators
            case TokenType.PLUS:
                if left_type not in {
                    PrimitiveType(TokenType.INT),
                    PrimitiveType(TokenType.FLOAT),
                    PrimitiveType(TokenType.STR),
                }:
                    raise TypeError(
                        f"Invalid operand types for {node.operator}: {left_type}"
                    )
                return left_type
            case TokenType.MINUS | TokenType.MULTIPLY | TokenType.DIVIDE:
                if left_type not in {
                    PrimitiveType(TokenType.INT),
                    PrimitiveType(TokenType.FLOAT),
                }:
                    raise TypeError(
                        f"Invalid operand types for {node.operator}: {left_type}"
                    )
                return left_type
            # Comparison operators
            case TokenType.EQUAL | TokenType.NOT_EQUAL:
                return PrimitiveType(TokenType.BOOL)
            case TokenType.LT | TokenType.GT | TokenType.LTE | TokenType.GTE:
                if left_type not in {
                    PrimitiveType(TokenType.INT),
                    PrimitiveType(TokenType.FLOAT),
                }:
                    raise TypeError(
                        f"Invalid operand types for {node.operator}: {left_type}"
                    )

                return PrimitiveType(TokenType.BOOL)
            # Logical operators
            case TokenType.LOGICAL_AND | TokenType.LOGICAL_OR:
                if left_type != PrimitiveType(TokenType.BOOL):
                    raise TypeError(
                        f"Invalid operand type for {node.operator}: {left_type}"
                    )
                return PrimitiveType(TokenType.BOOL)

            case _:
                raise TypeError(f"Invalid use of operator: {node.operator}")

    def analyze_unary_expression(self, node: UnaryExpression) -> VarType:
        operand_type = self.analyzer.analyze(node.operand)

        match node.operator:
            case TokenType.LOGICAL_NOT:
                if operand_type != PrimitiveType(TokenType.BOOL):
                    raise TypeError(
                        f"Invalid operand type for {node.operator}: {operand_type}"
                    )
                return PrimitiveType(TokenType.BOOL)
            case TokenType.MINUS:
                if operand_type not in {
                    PrimitiveType(TokenType.INT),
                    PrimitiveType(TokenType.FLOAT),
                }:
                    raise TypeError(
                        f"Invalid operand type for {node.operator}: {operand_type}"
                    )
                return operand_type
            case TokenType.INCREMENT | TokenType.DECREMENT:
                if not self._is_assignable(node.operand):
                    raise TypeError(f"Invalid assignment target for {node.operator}")
                if operand_type not in {
                    PrimitiveType(TokenType.INT),
                    PrimitiveType(TokenType.FLOAT),
                }:
                    raise TypeError(
                        f"Invalid operand type for {node.operator}: {operand_type}"
                    )
                return operand_type

            case _:
                raise TypeError(f"Invalid use of operator: {node.operator}")

    def analyze_assignment_expression(self, node: AssignmentExpression) -> VarType:
        if not isinstance(
            node.left, (Identifier, IndexExpression, MemberAccessExpression)
        ):
            raise TypeError("Invalid assignment target")

        left_type = self.analyzer.analyze(node.left)
        right_type = self.analyzer.analyze(node.right)

        if left_type != right_type:
            raise TypeError(
                f"Type mismatch in assignment expression: {left_type} != {right_type}"
            )

        return left_type

    def analyze_identifier(self, node: Identifier) -> VarType:
        symbol = self.analyzer.symbol_table.lookup(node.name, True)
        if not symbol:
            symbol = self.analyzer.symbol_table.lookup(node.name)
            if not symbol or not isinstance(symbol.var_type, FunctionType):
                raise NameError(f"Variable `{node.name}` not declared")

        return symbol.var_type

    def analyze_function_call_expression(self, node: FunctionCallExpression) -> VarType:
        function_type: FunctionType
        if isinstance(node.callee, Identifier):
            symbol = self.analyzer.symbol_table.lookup(node.callee.name)
            if symbol is None:
                raise NameError(f"Function `{node.callee.name}` not declared")
            if not isinstance(symbol.var_type, FunctionType):
                raise TypeError(f"`{node.callee.name}` is not a function")
            function_type = symbol.var_type
        else:
            node_type = self.analyzer.analyze(node.callee)
            if not isinstance(node_type, FunctionType):
                raise TypeError(
                    "Callee expression does not evaluate to a function type"
                )
            function_type = node_type

        if len(node.args) != len(function_type.param_types):
            if isinstance(node.callee, Identifier):
                raise TypeError(
                    f"Function `{node.callee.name}` expects "
                    f"{len(function_type.param_types)} arguments, got {len(node.args)}"
                )
            raise TypeError(
                f"Function expects {len(function_type.param_types)} "
                f"arguments, got {len(node.args)}"
            )

        for arg, (_, param_type) in zip(node.args, function_type.param_types):
            arg_type = self.analyzer.analyze(arg)
            if arg_type != param_type:
                raise TypeError(
                    f"Argument type `{arg_type}` does not "
                    f"match parameter type `{param_type}`"
                )

        return function_type.return_type

    def analyze_index_expression(self, node: IndexExpression) -> VarType:
        index_type = self.analyzer.analyze(node.index)
        if index_type != PrimitiveType(TokenType.INT):
            raise TypeError("Array index must be an integer")

        array_type = self.analyzer.analyze(node.array)
        if not isinstance(array_type, ArrayType):
            raise TypeError("Indexing non-array type")

        return array_type.element_type

    def analyze_member_access_expression(self, node: MemberAccessExpression) -> VarType:
        composite_type = self.analyzer.analyze(node.composite)
        if not isinstance(composite_type, CompositeType):
            raise TypeError(f"Type `{composite_type}` does not have members")
        member_type = composite_type.attributes.get(node.member.name)

        if member_type is None:
            raise TypeError(
                f"Member `{node.member.name}` is not defined on type `{composite_type}`"
            )

        return member_type

    def analyze_method_call_expression(self, node: MethodCallExpression) -> VarType:
        composite_type = self.analyzer.analyze(node.composite)
        if not isinstance(composite_type, CompositeType):
            raise TypeError(f"Type `{composite_type}` does not have methods")
        method_type = composite_type.methods.get(node.method.name)

        if method_type is None:
            raise TypeError(
                f"Method `{node.method.name}` is not defined on type `{composite_type}`"
            )

        if len(node.args) != len(method_type.param_types):
            raise TypeError(
                f"Method `{node.method.name}` expects {len(method_type.param_types)} "
                f"arguments, got {len(node.args)}"
            )

        for arg, (_, param_type) in zip(node.args, method_type.param_types):
            arg_type = self.analyzer.analyze(arg)
            if arg_type != param_type:
                raise TypeError(
                    f"Argument type `{arg_type}` does not "
                    f"match parameter type `{param_type}`"
                )

        return method_type.return_type

    # Literals
    def analyze_numeric_literal(self, node: NumericLiteral) -> VarType:
        if isinstance(node.value, int):
            return PrimitiveType(TokenType.INT)

        return PrimitiveType(TokenType.FLOAT)

    def analyze_string_literal(self, node: StringLiteral) -> VarType:
        return PrimitiveType(TokenType.STR)

    def analyze_boolean_literal(self, node: BooleanLiteral) -> VarType:
        return PrimitiveType(TokenType.BOOL)

    def analyze_null_literal(self, node: NullLiteral) -> VarType:
        return PrimitiveType(TokenType.NULL)

    def analyze_array_literal(self, node: ArrayLiteral) -> VarType:
        if not node.elements:
            return ArrayType(VoidType())

        element_type = self.analyzer.analyze(node.elements[0])
        for element in node.elements:
            if self.analyzer.analyze(element) != element_type:
                raise TypeError("Invalid element type in array literal")

        return ArrayType(element_type, len(node.elements))

    def analyze_set_literal(self, node: SetLiteral) -> VarType:
        if not node.elements:
            return SetType(VoidType())

        element_type = self.analyzer.analyze(node.elements[0])
        for element in node.elements:
            if self.analyzer.analyze(element) != element_type:
                raise TypeError("Invalid element type in set literal")

        return SetType(element_type)

    def analyze_map_literal(self, node: MapLiteral) -> VarType:
        if not node.elements:
            return MapType(VoidType(), VoidType())

        key, val = node.elements[0]
        key_type = self.analyzer.analyze(key)
        value_type = self.analyzer.analyze(val)

        for k, v in node.elements:
            if self.analyzer.analyze(k) != key_type:
                raise TypeError("Invalid key type in map literal")
            if self.analyzer.analyze(v) != value_type:
                raise TypeError("Invalid value type in map literal")

        return MapType(key_type, value_type)

    def analyze_entity_literal(self, node: EntityLiteral) -> VarType:
        template_symbol = self.analyzer.symbol_table.lookup(node.template.name, False)
        if not template_symbol:
            raise NameError(f"Template `{node.template}` not found")
        template = template_symbol.var_type
        if not isinstance(template, TemplateType):
            raise TypeError(f"`{node.template}` is not a template")

        for key, value in node.attributes.items():
            if key not in template.attributes:
                raise NameError(
                    f"Attribute `{key}` not defined in template `{node.template.name}`"
                )
            entity_member_type = self.analyzer.analyze(value)
            template_member_type = template.attributes[key]

            if entity_member_type != template_member_type:
                raise TypeError(
                    f"Type mismatch for attribute `{key}`: "
                    f"`{template.attributes[key]}` != `{entity_member_type}`"
                )

        return template

    def analyze_function_literal(self, node: FunctionLiteral) -> VarType:
        self.analyzer.symbol_table.enter_scope(node)

        for param_name, param_type in node.parameters:
            self.analyzer.symbol_table.define(param_name, param_type)

        return_type = VoidType()
        for statement in node.body.statements:
            if not isinstance(statement, ReturnStatement):
                continue
            return_type = self.analyzer.statement_analyzer.get_return_type(statement)

        self.analyzer.statement_analyzer.analyze_block_statement(node.body)

        self.analyzer.symbol_table.exit_scope()

        return FunctionType(return_type, node.parameters)

    # Helpers
    def _is_assignable(self, node: Expression) -> bool:
        if isinstance(node, Identifier):
            return True

        if isinstance(node, IndexExpression):
            return self._is_assignable(node.array)

        return False
