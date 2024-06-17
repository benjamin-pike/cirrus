from frontend.semantic.types import *
from frontend.semantic.types import VarType
from frontend.semantic.typing import *
from frontend.syntax.ast import *


class ExpressionAnalyzer(ExpressionAnalyzerABC):
    """Class that provides methods for analyzing the expression semantics."""

    def __init__(self, analyzer: SemanticAnalyzerABC) -> None:
        self.analyzer = analyzer

    def analyze_binary_expression(self, node: BinaryExpression) -> VarType:
        """Analyses a BinaryExpression node, checking the operand types.

        Args:
            node (BinaryExpression): The BinaryExpression node to analyse.

        Returns:
            VarType: The type of the binary expression.

        Raises:
            TypeError: If the operand types do not match the operator.
            TypeError: If the operator is invalid.
        """
        left_type = self.analyzer.analyze(node.left)
        right_type = self.analyzer.analyze(node.right)

        if left_type != right_type:
            raise TypeError(
                f"Type mismatch in binary expression: {left_type} != {right_type}"
            )

        match node.operator:
            # Arithmetic operators
            case (
                TokenType.PLUS | TokenType.MINUS | TokenType.MULTIPLY | TokenType.DIVIDE
            ):
                if left_type not in {
                    PrimitiveType(TokenType.INT),
                    PrimitiveType(TokenType.FLOAT),
                    PrimitiveType(TokenType.STRING),
                }:
                    raise TypeError(
                        f"Invalid operand types for {node.operator}: {left_type}"
                    )
                return left_type
            # Comparison operators
            case (
                TokenType.EQUAL
                | TokenType.NOT_EQUAL
                | TokenType.LT
                | TokenType.GT
                | TokenType.LTE
                | TokenType.GTE
            ):
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
        """Analyses a UnaryExpression node, checking the operand type.

        Args:
            node (UnaryExpression): The UnaryExpression node to analyse.

        Returns:
            VarType: The type of the unary expression.

        Raises:
            TypeError: If the operand type does not match the operator.
            TypeError: If the operator is invalid.
        """
        operand_type = self.analyzer.analyze(node.operand)

        match node.operator:
            case TokenType.LOGICAL_NOT:
                if operand_type != PrimitiveType(TokenType.BOOL):
                    raise TypeError(
                        f"Invalid operand type for {node.operator}: {operand_type}"
                    )
                return PrimitiveType(TokenType.BOOL)
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
        """Analyses an AssignmentExpression node, checking the assigned value type.

        Args:
            node (AssignmentExpression): The AssignmentExpression node to analyse.

        Returns:
            VarType: The type of the assignment expression.

        Raises:
            NameError: If the variable is not declared.
            TypeError: If the variable type does not match the assigned value type.
            TypeError: If the assignment target is invalid.
        """
        if isinstance(node.left, Identifier):
            var_name = node.left.name
        elif isinstance(node.left, IndexExpression) and isinstance(
            node.left.array, Identifier
        ):
            var_name = node.left.array.name
        else:
            raise TypeError("Invalid assignment target")

        if not self.analyzer.symbol_table.lookup(var_name, True):
            raise NameError(f"Variable `{var_name}` not declared")

        left_type = self.analyzer.analyze(node.left)
        right_type = self.analyzer.analyze(node.right)

        if left_type != right_type:
            raise TypeError(
                f"Type mismatch in assignment expression: {left_type} != {right_type}"
            )

        return left_type

    def analyze_numeric_literal(self, node: NumericLiteral) -> VarType:
        """Analyses a NumericLiteral node, returning its type.

        Args:
            node (NumericLiteral): The NumericLiteral node to analyse.

        Returns:
            VarType: The type of the numeric literal.
        """
        if isinstance(node.value, int):
            return PrimitiveType(TokenType.INT)

        return PrimitiveType(TokenType.FLOAT)

    def analyze_string_literal(self, node: StringLiteral) -> VarType:
        """Analyses a StringLiteral node, returning its type.

        Args:
            node (StringLiteral): The StringLiteral node to analyse.

        Returns:
            VarType: The type of the string literal.
        """
        return PrimitiveType(TokenType.STRING)

    def analyze_boolean_literal(self, node: BooleanLiteral) -> VarType:
        """Analyses a BooleanLiteral node, returning its type.

        Args:
            node (BooleanLiteral): The BooleanLiteral node to analyse.

        Returns:
            VarType: The type of the boolean literal.
        """
        return PrimitiveType(TokenType.BOOL)

    def analyze_null_literal(self, node: NullLiteral) -> VarType:
        """Analyses a NullLiteral node, returning its type.

        Args:
            node (NullLiteral): The NullLiteral node to analyse.

        Returns:
            VarType: The type of the null literal.
        """
        return PrimitiveType(TokenType.NULL)

    def analyze_identifier(self, node: Identifier) -> VarType:
        """Analyses an Identifier node, checking if the
        variable is declared and returning its declared type.

        Args:
            node (Identifier): The Identifier node to analyse.

        Returns:
            VarType: The declared type of the identifier.

        Raises:
            NameError: If the identifier is not declared.
        """
        symbol = self.analyzer.symbol_table.lookup(node.name, True)
        if not symbol:
            raise NameError(f"Variable `{node.name}` not declared")

        return symbol.var_type

    def analyze_function_call_expression(self, node: FunctionCallExpression) -> VarType:
        """Analyses a FunctionCallExpression node,
        checking the function declaration and argument types.

        Args:
            node (FunctionCallExpression): The FunctionCallExpression node to analyse.

        Raises:
            NameError: If the function is not declared.
            TypeError: If the function is not a function type.
            TypeError:
                If the number of arguments does not match the function declaration.
            TypeError: If the argument types do not match the function declaration.

        Returns:
            VarType: The return type of the function.
        """

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

    def analyze_array_literal(self, node: ArrayLiteral) -> VarType:
        """Analyses an ArrayLiteral node, checking the element types.

        Args:
            node (ArrayLiteral): The ArrayLiteral node to analyse.

        Returns:
            VarType: The type of the array.

        Raises:
            TypeError: If the element types are invalid.
        """
        if not node.elements:
            return ArrayType(PrimitiveType(TokenType.NULL))

        element_type = self.analyzer.analyze(node.elements[0])
        for element in node.elements:
            if self.analyzer.analyze(element) != element_type:
                raise TypeError("Invalid element type in array literal")

        return ArrayType(element_type)

    def analyze_set_literal(self, node: SetLiteral) -> VarType:
        """Analyses a SetLiteral node, checking the element types.

        Args:
            node (SetLiteral): The SetLiteral node to analyse.

        Returns:
            VarType: The type of the set.

        Raises:
            TypeError: If the element types are invalid.
        """
        if not node.elements:
            return SetType(PrimitiveType(TokenType.NULL))

        element_type = self.analyzer.analyze(node.elements[0])
        for element in node.elements:
            if self.analyzer.analyze(element) != element_type:
                raise TypeError("Invalid element type in set literal")

        return SetType(element_type)

    def analyze_map_literal(self, node: MapLiteral) -> VarType:
        """Analyses a MapLiteral node, checking the key and value types.

        Args:
            node (MapLiteral): The MapLiteral node to analyse.

        Returns:
            VarType: The type of the map.

        Raises:
            TypeError: If the key types are invalid.
            TypeError: If the value types are invalid.
        """

        if not node.elements:
            return MapType(PrimitiveType(TokenType.NULL), PrimitiveType(TokenType.NULL))

        key, val = node.elements[0]
        key_type = self.analyzer.analyze(key)
        value_type = self.analyzer.analyze(val)

        for k, v in node.elements:
            if self.analyzer.analyze(k) != key_type:
                raise TypeError("Invalid key type in map literal")
            if self.analyzer.analyze(v) != value_type:
                raise TypeError("Invalid value type in map literal")

        return MapType(key_type, value_type)

    def analyze_index_expression(self, node: IndexExpression) -> VarType:
        """Analyses an IndexExpression node, checking the array and index types.

        Args:
            node (IndexExpression): The IndexExpression node to analyse.

        Returns:
            VarType: The type of the indexed value.

        Raises:
            TypeError: If the array index is not an integer.
            TypeError: If the array is not an array type.
        """

        index_type = self.analyzer.analyze(node.index)
        if index_type != PrimitiveType(TokenType.INT):
            raise TypeError("Array index must be an integer")

        array_type = self.analyzer.analyze(node.array)
        if not isinstance(array_type, ArrayType):
            raise TypeError("Indexing non-array type")

        return array_type.element_type

    def analyze_member_access_expression(self, node: MemberAccessExpression) -> VarType:
        """Not implemented."""
        raise NotImplementedError

    def analyze_method_call_expression(self, node: MethodCallExpression) -> VarType:
        """Analyses a MethodCallExpression node,
        checking the object type and method name.

        Args:
            node (MethodCallExpression): The MethodCallExpression node to analyse.

        Returns:
            VarType: The return type of the method.

        Raises:
            TypeError: If the object type does not have the method.
            TypeError: If the argument types do not match the method declaration.
        """
        obj_type = self.analyzer.analyze(node.obj)
        if not isinstance(obj_type, (SetType, MapType)):
            raise TypeError(f"Type `{obj_type}` does not have methods")
        method_type = obj_type.methods.get(node.method.name)

        if method_type is None:
            raise TypeError(
                f"Method `{node.method.name}` is not defined on type `{obj_type}`"
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

    # Helpers
    def _is_assignable(self, node: Expression) -> bool:
        """Checks if an expression is a valid assignment target.

        Args:
            node (Expression): The expression to check.

        Returns:
            bool: True if the expression is assignable, otherwise False.
        """
        if isinstance(node, Identifier):
            return True

        if isinstance(node, IndexExpression):
            return self._is_assignable(node.array)

        return False
