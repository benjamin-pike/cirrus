# pyright: reportReturnType=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false


from llvmlite import ir
from frontend.ir.helpers import get_ir_type
from frontend.ir.typing import ExpressionGeneratorABC, IRGeneratorABC
from frontend.ir.types import *
from frontend.syntax.ast import *
from frontend.semantic.types import PrimitiveType


class ExpressionGenerator(ExpressionGeneratorABC):
    """The ExpressionGenerator generates LLVM intermediate representation (IR)
    code for expressions in the AST. It traverses the AST and generates IR for
    each expression node."""

    def __init__(self, generator: IRGeneratorABC):
        self.generator = generator

    def generate_numeric_literal(self, node: NumericLiteral) -> ir.Value:
        """Generate LLVM IR for a numeric literal.

        Args:
            node (NumericLiteral): The numeric literal node

        Returns:
            ir.Value: The LLVM IR value, int or float (constant)
        """
        if isinstance(node.value, int):
            return ir.Constant(IRType.int(32), node.value)
        return ir.Constant(IRType.float(), node.value)

    def generate_string_literal(self, node: StringLiteral) -> ir.Value:
        """Generate LLVM IR for a string literal.

        Args:
            node (StringLiteral): The string literal node

        Returns:
            ir.Value: The bitcasted global variable pointer to the string literal
        """
        str_val = node.value.encode("utf8") + b"\0"
        str_const = ir.Constant(
            ir.ArrayType(IRType.int(8), len(str_val)), bytearray(str_val)
        )

        str_global = ir.GlobalVariable(
            self.generator.module, str_const.type, name=node.id
        )
        str_global.linkage = "internal"
        str_global.global_constant = True
        str_global.initializer = str_const

        return self.generator.builder.bitcast(str_global, IRType.int(8).as_pointer())

    def generate_boolean_literal(self, node: BooleanLiteral) -> ir.Value:
        """Generate LLVM IR for a boolean literal.

        Args:
            node (BooleanLiteral): The boolean literal node

        Returns:
            ir.Value: The LLVM IR bool value (constant)
        """
        return ir.Constant(IRType.bool(), node.value)

    def generate_null_literal(self) -> ir.Value:
        """Generate LLVM IR for a null literal.

        Returns:
            ir.Value: The LLVM null pointer value (constant)
        """
        return ir.Constant(IRType.null(), None)

    def generate_array_literal(self, node: ArrayLiteral) -> ir.Value:
        """Generate LLVM IR for an array literal.

        Args:
            node (ArrayLiteral): The array literal node

        Returns:
            ir.Value: The LLVM IR value (pointer to array)
        """
        # FIX: Change arrays to store elements as pointers
        array_type = get_ir_type(node.type).pointee
        array_ptr = self.generator.builder.alloca(array_type)

        for i, element in enumerate(node.elements):
            element_ptr = self.generator.builder.gep(
                array_ptr,
                [ir.Constant(IRType.int(32), 0), ir.Constant(IRType.int(32), i)],
            )
            self.generator.builder.store(
                self.generator.generate_expression(element), element_ptr
            )

        return array_ptr

    def generate_identifier(self, node: Identifier) -> ir.Value:
        """Generate LLVM IR for an identifier.

        Args:
            node (Identifier): The identifier node

        Returns:
            ir.Value: The LLVM IR value (variable or function)
        """
        symbol = self.generator.symbol_table.get(node.name)
        if not symbol:
            raise NameError(f"Variable '{node.name}' not found")

        if isinstance(symbol, ir.Function):
            return symbol

        return self.generator.builder.load(symbol)

    def generate_unary_expression(self, node: UnaryExpression) -> ir.Value:
        """Generate LLVM IR for a unary expression.

        Args:
            node (UnaryExpression): The unary expression node

        Returns:
            ir.Value: The LLVM IR value resulting from the unary operation
        """
        operand = self.generator.generate_expression(node.operand)

        match node.operator:
            case TokenType.LOGICAL_NOT:
                return self.generator.builder.not_(operand)
            case TokenType.MINUS:
                return self.generator.builder.neg(operand)
            case TokenType.INCREMENT:
                incremented = self.generator.builder.add(
                    operand, ir.Constant(IRType.int(32), 1)
                )
                self.generator.builder.store(
                    incremented, self.generator.symbol_table[node.operand.name]
                )
                if node.position == "POST":
                    return operand
                return incremented
            case TokenType.DECREMENT:
                decremented = self.generator.builder.sub(
                    operand, ir.Constant(IRType.int(32), 1)
                )
                self.generator.builder.store(
                    decremented, self.generator.symbol_table[node.operand.name]
                )
                if node.position == "POST":
                    return operand
                return decremented
            case _:
                raise NotImplementedError(
                    f"Unary operator '{node.operator}' not implemented"
                )

    def generate_binary_expression(self, node: BinaryExpression) -> ir.Value:
        """Generate LLVM IR for a binary expression.

        Args:
            node (BinaryExpression): The binary expression node

        Returns:
            ir.Value: The LLVM IR value resulting from the binary operation
        """
        left = self.generator.generate_expression(node.left)
        right = self.generator.generate_expression(node.right)

        if node.operator == TokenType.LOGICAL_AND:
            return self.generator.builder.and_(left, right)
        if node.operator == TokenType.LOGICAL_OR:
            return self.generator.builder.or_(left, right)

        if node.left.type == PrimitiveType(TokenType.INT):
            match node.operator:
                case TokenType.PLUS:
                    return self.generator.builder.add(left, right)
                case TokenType.MINUS:
                    return self.generator.builder.sub(left, right)
                case TokenType.MULTIPLY:
                    return self.generator.builder.mul(left, right)
                case TokenType.DIVIDE:
                    return self.generator.builder.sdiv(left, right)
                case TokenType.EQUAL:
                    return self.generator.builder.icmp_signed("==", left, right)
                case TokenType.NOT_EQUAL:
                    return self.generator.builder.icmp_signed("!=", left, right)
                case TokenType.LT:
                    return self.generator.builder.icmp_signed("<", left, right)
                case TokenType.GT:
                    return self.generator.builder.icmp_signed(">", left, right)
                case TokenType.LTE:
                    return self.generator.builder.icmp_signed("<=", left, right)
                case TokenType.GTE:
                    return self.generator.builder.icmp_signed(">=", left, right)
                case _:
                    raise NotImplementedError(
                        f"Binary operator `{node.operator}` for int not implemented"
                    )

        if node.left.type == PrimitiveType(TokenType.FLOAT):
            match node.operator:
                case TokenType.PLUS:
                    return self.generator.builder.fadd(left, right)
                case TokenType.MINUS:
                    return self.generator.builder.fsub(left, right)
                case TokenType.MULTIPLY:
                    return self.generator.builder.fmul(left, right)
                case TokenType.DIVIDE:
                    return self.generator.builder.fdiv(left, right)
                case TokenType.EQUAL:
                    return self.generator.builder.fcmp_ordered("==", left, right)
                case TokenType.NOT_EQUAL:
                    return self.generator.builder.fcmp_ordered("!=", left, right)
                case TokenType.LT:
                    return self.generator.builder.fcmp_ordered("<", left, right)
                case TokenType.GT:
                    return self.generator.builder.fcmp_ordered(">", left, right)
                case TokenType.LTE:
                    return self.generator.builder.fcmp_ordered("<=", left, right)
                case TokenType.GTE:
                    return self.generator.builder.fcmp_ordered(">=", left, right)
                case _:
                    raise NotImplementedError(
                        f"Binary operator `{node.operator}` for float not implemented"
                    )

        if node.left.type == PrimitiveType(TokenType.STR):
            match node.operator:
                case TokenType.PLUS:
                    return self._concat_strings(left, right)
                case TokenType.EQUAL:
                    return self._compare_strings(left, right, "==")
                case TokenType.NOT_EQUAL:
                    return self._compare_strings(left, right, "!=")
                case _:
                    raise NotImplementedError(
                        f"Binary operator `{node.operator}` for str not implemented"
                    )

        raise NotImplementedError(
            f"Binary expression for type `{node.left.type}` not implemented"
        )

    def generate_assignment_expression(self, node: AssignmentExpression) -> ir.Value:
        """Generate LLVM IR for an assignment expression.

        Args:
            node (AssignmentExpression): The assignment expression node

        Returns:
            ir.Value: The LLVM IR value of the assigned expression
        """
        value = self.generator.generate_expression(node.right)
        assert isinstance(node.left, Identifier)  # FIX: Support object attr assignment
        target = self.generator.symbol_table[node.left.name]
        self.generator.builder.store(value, target)

        return value

    def generate_index_expression(self, node: IndexExpression) -> ir.Value:
        """Generate LLVM IR for an index expression.

        Args:
            node (IndexExpression): The index expression node

        Returns:
            ir.Value: The LLVM IR value of the indexed element
        """
        array = self.generator.generate_expression(node.array)
        index = self.generator.generate_expression(node.index)

        element_ptr = self.generator.builder.gep(
            array, [ir.Constant(IRType.int(32), 0), index]
        )

        return self.generator.builder.load(element_ptr)

    def generate_function_call_expression(
        self, node: FunctionCallExpression
    ) -> ir.Value:
        """Generate LLVM IR for a function call expression.

        Args:
            node (FunctionCallExpression): The function call expression node

        Returns:
            ir.Value: The LLVM IR value of the function call result
        """
        callee = self.generator.generate_expression(node.callee)

        args = []
        for arg in node.args:
            generated = self.generator.generate_expression(arg)
            if isinstance(generated, ir.AllocaInstr):
                generated = self.generator.builder.load(generated)
            args.append(generated)

        return self.generator.builder.call(callee, args)

    # Helper methods
    def _compare_strings(
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

        strcmp_res = self.generator.builder.call(
            self.generator.module.get_global("strcmp"),
            [left, right],
            name=f"str_cmp_{cmp_op}",
        )

        return self.generator.builder.icmp_signed(
            cmp_op,
            strcmp_res,
            ir.Constant(IRType.int(32), 0),
        )

    def _concat_strings(self, left: ir.Value, right: ir.Value) -> ir.Value:
        """Generate LLVM IR to concatenate two strings.

        Args:
            left (ir.Value): The left string to concatenate
            right (ir.Value): The right string to concatenate

        Returns:
            ir.Value: The pointer to the concatenated string
        """
        left_len = self.generator.builder.call(
            self.generator.module.get_global("strlen"), [left], name="left_len"
        )
        right_len = self.generator.builder.call(
            self.generator.module.get_global("strlen"), [right], name="right_len"
        )

        total_len = self.generator.builder.add(left_len, right_len)
        total_len = self.generator.builder.add(
            total_len, ir.Constant(IRType.int(32), 1)
        )

        concat_str = self.generator.builder.call(
            self.generator.module.get_global("malloc"), [total_len], name="concat_str"
        )

        self.generator.builder.call(
            self.generator.module.get_global("strcpy"),
            [concat_str, left],
            name="copy_left",
        )

        self.generator.builder.call(
            self.generator.module.get_global("strcat"),
            [concat_str, right],
            name="concat_right",
        )

        return concat_str
