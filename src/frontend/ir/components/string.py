# pyright: reportReturnType=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false


from llvmlite import ir
from frontend.ir.types import IRType
from frontend.ir.typing import IRGeneratorABC, StringGeneratorABC
from frontend.syntax.ast import StringLiteral


class StringGenerator(StringGeneratorABC):
    """Generates LLVM IR for string literals and associated operations."""

    def __init__(self, generator: IRGeneratorABC):
        self.generator = generator

    def generate_string_literal(self, node: StringLiteral) -> ir.Value:
        str_val = node.value.encode("utf8") + b"\0"
        str_const = ir.Constant(
            ir.ArrayType(IRType.int(8), len(str_val)), bytearray(str_val)
        )

        str_global = ir.GlobalVariable(self.generator.module, str_const.type, node.id)
        str_global.linkage = "internal"
        str_global.global_constant = True
        str_global.initializer = str_const

        return self.generator.builder.bitcast(str_global, IRType.pointer(None))

    def compare_strings(
        self, left: ir.Value, right: ir.Value, cmp_op: str
    ) -> ir.Instruction:
        strcmp_res = self.generator.builder.call(
            self.generator.module.get_global("strcmp"), [left, right]
        )

        return self.generator.builder.icmp_signed(
            cmp_op,
            strcmp_res,
            ir.Constant(IRType.int(32), 0),
        )

    def concat_strings(self, left: ir.Value, right: ir.Value) -> ir.Value:
        left_len = self.generator.builder.call(
            self.generator.module.get_global("strlen"), [left]
        )
        right_len = self.generator.builder.call(
            self.generator.module.get_global("strlen"), [right]
        )

        total_len = self.generator.builder.add(left_len, right_len)
        total_len = self.generator.builder.add(
            total_len, ir.Constant(IRType.int(32), 1)
        )

        concat_str = self.generator.builder.call(
            self.generator.module.get_global("malloc"), [total_len]
        )

        self.generator.builder.call(
            self.generator.module.get_global("strcpy"), [concat_str, left]
        )

        self.generator.builder.call(
            self.generator.module.get_global("strcat"), [concat_str, right]
        )

        return concat_str
