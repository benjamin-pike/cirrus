# pyright: reportReturnType=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false


from llvmlite import ir
from frontend.ir.types import IRType
from frontend.ir.typing import IRGeneratorABC
from frontend.syntax.ast import StringLiteral


class StringGenerator:
    """Generates LLVM IR for string literals and associated operations."""

    def __init__(self, generator: IRGeneratorABC):
        self.generator = generator

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

    def concat_strings(self, left: ir.Value, right: ir.Value) -> ir.Value:
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
