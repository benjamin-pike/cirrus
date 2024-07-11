# pyright: reportReturnType=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false


from llvmlite import ir
from frontend.ir.components.array import ArrayGenerator
from frontend.ir.components.string import StringGenerator
from frontend.ir.typing import ExpressionGeneratorABC, IRGeneratorABC
from frontend.ir.types import *
from frontend.syntax.ast import *
from frontend.semantic.types import PrimitiveType


class ExpressionGenerator(ExpressionGeneratorABC):
    """Generates LLVM intermediate representation code for expression AST nodes."""

    def __init__(self, generator: IRGeneratorABC):
        self.generator = generator
        self.string_generator = StringGenerator(generator)
        self.array_generator = ArrayGenerator(generator)

    def __getattr__(self, name: str):
        if hasattr(self.string_generator, name):
            return getattr(self.string_generator, name)
        if hasattr(self.array_generator, name):
            return getattr(self.array_generator, name)
        raise AttributeError(f"ExpressionGenerator object has no attribute `{name}`")

    def generate_numeric_literal(self, node: NumericLiteral) -> ir.Value:
        if isinstance(node.value, int):
            return ir.Constant(IRType.int(32), node.value)
        return ir.Constant(IRType.float(), node.value)

    def generate_boolean_literal(self, node: BooleanLiteral) -> ir.Value:
        return ir.Constant(IRType.bool(), node.value)

    def generate_string_literal(self, node: StringLiteral) -> ir.Value:
        return self.string_generator.generate_string_literal(node)

    def generate_null_literal(self, _node: NullLiteral) -> ir.Value:
        return ir.Constant(IRType.null(), None)

    def generate_identifier(self, node: Identifier) -> ir.Value:
        symbol = self.generator.symbol_table.get(node.name)
        if not symbol:
            raise NameError(f"Variable '{node.name}' not found")

        if isinstance(symbol, ir.Function):
            return symbol

        return self.generator.builder.load(symbol)

    def generate_unary_expression(self, node: UnaryExpression) -> ir.Value:
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
                    return self.string_generator.concat_strings(left, right)
                case TokenType.EQUAL:
                    return self.string_generator.compare_strings(left, right, "==")
                case TokenType.NOT_EQUAL:
                    return self.string_generator.compare_strings(left, right, "!=")
                case _:
                    raise NotImplementedError(
                        f"Binary operator `{node.operator}` for str not implemented"
                    )

        raise NotImplementedError(
            f"Binary expression for type `{node.left.type}` not implemented"
        )

    def generate_assignment_expression(self, node: AssignmentExpression) -> ir.Value:
        value = self.generator.generate_expression(node.right)
        # FIX: Support composite attr assignment
        assert isinstance(node.left, Identifier)
        target = self.generator.symbol_table[node.left.name]
        self.generator.builder.store(value, target)

        return value

    def generate_function_call_expression(
        self, node: FunctionCallExpression
    ) -> ir.Value:
        callee = self.generator.generate_expression(node.callee)

        args = []
        for arg in node.args:
            generated = self.generator.generate_expression(arg)
            if isinstance(generated, ir.AllocaInstr):
                generated = self.generator.builder.load(generated)
            args.append(generated)

        return self.generator.builder.call(callee, args)

    def generate_method_call_expression(self, node: MethodCallExpression) -> ir.Value:
        if isinstance(node.composite.type, ArrayType):
            return self.array_generator.generate_array_method_call(node)

        raise NotImplementedError("Method call expression not implemented")
