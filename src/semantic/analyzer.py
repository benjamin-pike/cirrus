from typing import *
from lexer.tokens import TokenType
from semantic.symbol import SymbolTable
from semantic.types import PrimitiveType, InferType, VarType, ArrayType, VoidType
from syntax.ast import *
from lib.helpers import is_iterable, pascal_to_snake_case

class SemanticAnalyzer:
    """
    The SemanticAnalyzer class performs semantic analysis by traversing the AST and ensuring
    that all variables and functions are declared before use and that all types are correct.
    """

    def __init__(self) -> None:
        self.symbol_table = SymbolTable()

    def analyze(self, node: Node) -> VarType:
        """ Analyses a node in the AST.

        Args:
            node (Node): The AST node to analyse.

        Returns:
            VarType: The type of the node.
        """
        method_name = f'analyze_{pascal_to_snake_case(type(node).__name__)}'
        analyze = getattr(self, method_name, self.analyze_generic)
        return analyze(node)

    def analyze_generic(self, node: Node) -> VarType:
        """ Called if no explicit analyzer function exists for a node. Recursively analyses children.

        Args:
            node (Node): The AST node to analyse.

        Returns:
            VarType: The type of the node.
        """
        for attr_value in vars(node).values():
            if isinstance(attr_value, Node):
                self.analyze(attr_value)
            elif is_iterable(attr_value):
                for item in attr_value:
                    if isinstance(item, Node):
                        self.analyze(item)

        return PrimitiveType(TokenType.VOID)

    def analyze_program(self, node: Program) -> VoidType:
        """ Starts semantic analysis from the root Program node.

        Args:
            node (Program): The Program node to analyse.

        Returns:
            VoidType: Void type.
        """
        self.symbol_table.enter_scope()
        for statement in node.body:
            self.analyze(statement)
        self.symbol_table.exit_scope()

        return VoidType()

    # Statements
    def analyze_variable_declaration(self, node: VariableDeclaration) -> VarType:
        """ Analyses a VariableDeclaration node, adding the variable to the symbol table and checking its type.

        Args:
            node (VariableDeclaration): The VariableDeclaration node to analyse.

        Returns:
            VarType: The type of the variable.
        """
        init_type = self.analyze(node.initializer)

        existing_symbol = self.symbol_table.lookup(node.name, True)

        if existing_symbol:
            existing_scope = self.symbol_table.get_scope(existing_symbol)
            if existing_scope == self.symbol_table.scopes[-1]:
                raise NameError(f'Cannot redeclare variable "{node.name}"')
            else:
                raise NameError(f'Cannot shadow existing variable "{node.name}"')

        if isinstance(node.var_type, InferType):
            node.var_type = init_type # Infer the variable type from the initializer
        if node.var_type != init_type:
            raise TypeError(f'Type mismatch for variable {node.name}: {node.var_type} != {init_type}')

        self.symbol_table.define(node.name, node.var_type)

        return node.var_type

    def analyze_function_declaration(self, node: FunctionDeclaration) -> VarType:
        """ Analyses a FunctionDeclaration node, adding the function to the symbol table and managing parameter scope.

        Args:
            node (FunctionDeclaration): The FunctionDeclaration node to analyse.

        Returns:
            VarType: The return type of the function.
        """
        if self.symbol_table.lookup(node.name, True):
            raise NameError(f'Cannot redeclare function "{node.name}"')

        self.symbol_table.define(node.name, node.function_type)

        self.symbol_table.enter_scope(node.function_type)
        for param_name, param_type in node.function_type.param_types:
            self.symbol_table.define(param_name, param_type)
        self.analyze(node.body)
        self.symbol_table.exit_scope()

        return node.function_type.return_type

    def analyze_block_statement(self, node: BlockStatement) -> VoidType:
        """ Analyses a BlockStatement node, managing scope entering and exiting.

        Args:
            node (BlockStatement): The BlockStatement node to analyse.

        Returns:
            VoidType: Void type.
        """
        self.symbol_table.enter_scope()
        for statement in node.statements:
            self.analyze(statement)
        self.symbol_table.exit_scope()

        return VoidType()

    def analyze_if_statement(self, node: IfStatement) -> VoidType:
        """ Analyses an IfStatement node, checking the condition and branches.

        Args:
            node (IfStatement): The IfStatement node to analyse.

        Returns:
            VoidType: Void type.
        """
        cond_type = self.analyze(node.condition)
        if cond_type != PrimitiveType(TokenType.BOOL):
            raise TypeError('Condition of if statement must be a boolean')
        self.analyze(node.then_block)
        if node.else_block:
            self.analyze(node.else_block)

        return VoidType()

    def analyze_while_statement(self, node: WhileStatement) -> VoidType:
        """ Analyses a WhileStatement node, checking the condition and body.

        Args:
            node (WhileStatement): The WhileStatement node to analyse.

        Returns:
            VarType: The type of the while statement.
        """
        cond_type = self.analyze(node.condition)
        if cond_type != PrimitiveType(TokenType.BOOL):
            raise TypeError('Condition of while statement must be a boolean')
        self.analyze(node.body)

        return VoidType()

    def analyze_range_statement(self, node: RangeStatement) -> VoidType:
        """ Analyses a RangeStatement node, adding the variable to the symbol table and checking types.

        Args:
            node (RangeStatement): The RangeStatement node to analyse.

        Returns:
            VoidType: Void type.
        """
        start_type = self.analyze(node.start)
        end_type = self.analyze(node.end)
        increment_type = self.analyze(node.increment)

        if (
            start_type != PrimitiveType(TokenType.INT) or
            end_type != PrimitiveType(TokenType.INT) or
            increment_type != PrimitiveType(TokenType.INT)
        ):
            raise TypeError('Range boundaries and increment must be integers')

        self.symbol_table.define(node.identifier, PrimitiveType(TokenType.INT))
        self.analyze(node.body)

        return VoidType()

    def analyze_each_statement(self, node: EachStatement) -> VoidType:
        """ Analyses an EachStatement node, adding the iteration variable to the symbol table
        and creating a new scope for its body.

        Args:
            node (EachStatement): The EachStatement node to analyse.

        Returns:
            VoidType: Void type.
        """
        iterable_type = self.analyze(node.iterable)
        if not isinstance(iterable_type, ArrayType):
            raise TypeError('Each statement requires an array type for iteration')
        element_type = iterable_type.element_type

        self.symbol_table.enter_scope()
        self.symbol_table.define(node.variable, element_type)
        self.analyze(node.body)
        self.symbol_table.exit_scope()

        return VoidType()

    def analyze_echo_statement(self, node: EchoStatement) -> VoidType:
        """ Analyses an EchoStatement node, checking the expression type.

        Args:
            node (EchoStatement): The EchoStatement node to analyse.

        Returns:
            VarType: The type of the echo statement.
        """
        self.analyze(node.expression)

        return VoidType()

    def analyze_return_statement(self, node: ReturnStatement) -> VarType:
        fn_scope = self.symbol_table.get_current_function_scope()
        if not fn_scope or not fn_scope.function_type:
            raise SyntaxError("Return statement is not valid outside of a function block")

        return_type = VoidType()
        if node.expression:
            return_type = self.analyze(node.expression)

        fn_return_type = fn_scope.function_type.return_type
        if return_type != fn_return_type:
            raise TypeError(f"Return type {return_type} does not match function return type {fn_return_type}")

        return return_type

    # Expressions
    def analyze_binary_expression(self, node: BinaryExpression) -> VarType:
        """ Analyses a BinaryExpression node, checking the operand types.

        Args:
            node (BinaryExpression): The BinaryExpression node to analyse.

        Returns:
            VarType: The type of the binary expression.
        """
        left_type = self.analyze(node.left)
        right_type = self.analyze(node.right)

        if left_type != right_type:
            raise TypeError(f'Type mismatch in binary expression: {left_type} != {right_type}')

        match node.operator:
            # Arithmetic operators
            case TokenType.PLUS | TokenType.MINUS | TokenType.MULTIPLY | TokenType.DIVIDE:
                if left_type not in {PrimitiveType(TokenType.INT), PrimitiveType(TokenType.FLOAT), PrimitiveType(TokenType.STRING)}:
                    raise TypeError(f'Invalid operand types for {node.operator}: {left_type}')
                return left_type
            # Comparison operators
            case TokenType.EQUAL | TokenType.NOT_EQUAL | TokenType.LT | TokenType.GT | TokenType.LTE | TokenType.GTE:
                return PrimitiveType(TokenType.BOOL)
            # Logical operators
            case TokenType.LOGICAL_AND | TokenType.LOGICAL_OR:
                if left_type != PrimitiveType(TokenType.BOOL):
                    raise TypeError(f'Invalid operand type for {node.operator}: {left_type}')
                return PrimitiveType(TokenType.BOOL)

            case _:
                raise TypeError(f'Invalid use of operator: {node.operator}')

    def analyze_unary_expression(self, node: UnaryExpression) -> VarType:
        """ Analyses a UnaryExpression node, checking the operand type.

        Args:
            node (UnaryExpression): The UnaryExpression node to analyse.

        Returns:
            VarType: The type of the unary expression.
        """
        operand_type = self.analyze(node.operand)

        match node.operator:
            case TokenType.LOGICAL_NOT:
                if operand_type != PrimitiveType(TokenType.BOOL):
                    raise TypeError(f'Invalid operand type for {node.operator}: {operand_type}')
                return PrimitiveType(TokenType.BOOL)
            case TokenType.INCREMENT | TokenType.DECREMENT:
                if not self._is_assignable(node.operand):
                    raise TypeError(f'Invalid assignment target for {node.operator}')
                if operand_type not in {PrimitiveType(TokenType.INT), PrimitiveType(TokenType.FLOAT)}:
                    raise TypeError(f'Invalid operand type for {node.operator}: {operand_type}')
                return operand_type

            case _:
                raise TypeError(f'Invalid use of operator: {node.operator}')

    def analyze_assignment_expression(self, node: AssignmentExpression) -> VarType:
        """ Analyses an AssignmentExpression node, checking the assigned value type.

        Args:
            node (AssignmentExpression): The AssignmentExpression node to analyse.

        Returns:
            VarType: The type of the assignment expression.
        """
        if isinstance(node.left, Identifier):
            var_name = node.left.name
        elif isinstance(node.left, IndexExpression) and isinstance(node.left.array, Identifier):
            var_name = node.left.array.name
        else:
            raise TypeError('Invalid assignment target')


        if not self.symbol_table.lookup(var_name, True):
            raise NameError(f'Variable "{var_name}" not declared')

        left_type = self.analyze(node.left)
        right_type = self.analyze(node.right)

        if left_type != right_type:
            raise TypeError(f'Type mismatch in assignment expression: {left_type} != {right_type}')

        return left_type

    def analyze_numeric_literal(self, node: NumericLiteral) -> VarType:
        """ Analyses a NumericLiteral node, returning its type.

        Args:
            node (NumericLiteral): The NumericLiteral node to analyse.

        Returns:
            VarType: The type of the numeric literal.
        """
        if isinstance(node.value, int):
            return PrimitiveType(TokenType.INT)
        else:
            return PrimitiveType(TokenType.FLOAT)

    def analyze_string_literal(self, node: StringLiteral) -> VarType:
        """ Analyses a StringLiteral node, returning its type.

        Args:
            node (StringLiteral): The StringLiteral node to analyse.

        Returns:
            VarType: The type of the string literal.
        """
        return PrimitiveType(TokenType.STRING)

    def analyze_boolean_literal(self, node: BooleanLiteral) -> VarType:
        """ Analyses a BooleanLiteral node, returning its type.

        Args:
            node (BooleanLiteral): The BooleanLiteral node to analyse.

        Returns:
            VarType: The type of the boolean literal.
        """
        return PrimitiveType(TokenType.BOOL)

    def analyze_null_literal(self, node: NullLiteral) -> VarType:
        """ Analyses a NullLiteral node, returning its type.

        Args:
            node (NullLiteral): The NullLiteral node to analyse.

        Returns:
            VarType: The type of the null literal.
        """
        return PrimitiveType(TokenType.NULL)

    def analyze_identifier(self, node: Identifier) -> VarType:
        """ Analyses an Identifier node, checking if the variable is declared and returning its declared type.

        Args:
            node (Identifier): The Identifier node to analyse.

        Returns:
            VarType: The declared type of the identifier.

        Raises:
            NameError: If the identifier is not declared.
        """
        symbol = self.symbol_table.lookup(node.name, True)
        if not symbol:
            raise NameError(f'Variable "{node.name}" not declared')

        return symbol.var_type

    def analyze_call_expression(self, node: CallExpression) -> VarType:
        symbol = self.symbol_table.lookup(node.callee.name)
        if symbol is None:
            raise NameError(f"Function {node.callee.name} not declared")
        if not isinstance(symbol.var_type, FunctionType):
            raise TypeError(f"{node.callee.name} is not a function")

        function_type = symbol.var_type
        if len(node.args) != len(function_type.param_types):
            raise TypeError(f"Function {node.callee.name} expects {len(function_type.param_types)} arguments, got {len(node.args)}")

        for arg, (_, param_type) in zip(node.args, function_type.param_types):
            arg_type = self.analyze(arg)
            if arg_type != param_type:
                raise TypeError(f"Argument type {arg_type} does not match parameter type {param_type}")

        return function_type.return_type

    def analyze_array_literal(self, node: ArrayLiteral) -> VarType:
        """ Analyses an ArrayLiteral node, checking the element types.

        Args:
            node (ArrayLiteral): The ArrayLiteral node to analyse.

        Returns:
            VarType: The type of the array.
        """
        if not node.elements:
            return ArrayType(PrimitiveType(TokenType.NULL))

        element_type = self.analyze(node.elements[0])
        for element in node.elements:
            if self.analyze(element) != element_type:
                raise TypeError('Inconsistent element types in array literal')

        return ArrayType(element_type)

    def analyze_index_expression(self, node: IndexExpression) -> VarType:
        """ Analyses an IndexExpression node, checking the array and index types.

        Args:
            node (IndexExpression): The IndexExpression node to analyse.

        Returns:
            VarType: The type of the indexed value.
        """

        index_type = self.analyze(node.index)
        if index_type != PrimitiveType(TokenType.INT):
            raise TypeError('Array index must be an integer')

        array_type = self.analyze(node.array)
        if not isinstance(array_type, ArrayType):
            raise TypeError('Indexing non-array type')

        return array_type.element_type

    def _is_assignable(self, node: Expression) -> bool:
        if isinstance(node, Identifier):
            return True

        if isinstance(node, IndexExpression):
            return self._is_assignable(node.array)

        return False
