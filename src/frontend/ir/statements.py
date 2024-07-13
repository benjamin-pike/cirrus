# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownArgumentType=false
# pyright: reportOptionalMemberAccess=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false

from llvmlite import ir
from frontend.ir.helpers import get_ir_type
from frontend.ir.types import IRType, NullPointerConst
from frontend.ir.typing import IRGeneratorABC, StatementGeneratorABC
from frontend.syntax.ast import *


class StatementGenerator(StatementGeneratorABC):
    """Generates LLVM intermediate representation code for statement AST nodes."""

    def __init__(self, generator: IRGeneratorABC):
        self.generator = generator

    def generate_expression_statement(self, node: ExpressionStatement) -> None:
        self.generator.generate_expression(node.expression)

    def generate_variable_declaration(self, node: VariableDeclaration) -> None:
        var_type = get_ir_type(node.var_type)
        initializer = self.generator.generate_expression(node.initializer)
        var_ptr = self.generator.builder.alloca(var_type)

        self.generator.builder.store(initializer, var_ptr)
        self.generator.symbol_table[node.name] = var_ptr

    def generate_function_declaration(self, node: FunctionDeclaration) -> None:
        func_type = get_ir_type(node.function_type)
        func = ir.Function(self.generator.module, func_type.pointee, node.name)
        self.generator.symbol_table[node.name] = func

        self.generator.enter_function(func)

        for i, (param_name, _) in enumerate(node.function_type.param_types):
            arg = func.args[i]
            arg_ptr = self.generator.builder.alloca(arg.type)
            self.generator.builder.store(arg, arg_ptr)
            self.generator.symbol_table[param_name] = arg_ptr

        self.generator.generate_statement(node.body)

        self.generator.exit_function()

    def generate_return_statement(self, node: ReturnStatement) -> None:
        if node.expression is None:
            self.generator.builder.ret_void()
            return

        retval = self.generator.generate_expression(node.expression)
        self.generator.builder.ret(retval)

    def generate_block_statement(self, node: BlockStatement) -> None:
        for statement in node.statements:
            self.generator.generate_statement(statement)

    def generate_if_statement(self, node: IfStatement) -> None:
        cond_val = self.generator.generate_expression(node.condition)
        then_block = self.generator.func.append_basic_block()
        else_block = self.generator.func.append_basic_block()
        merge_block = self.generator.func.append_basic_block()

        self.generator.builder.cbranch(cond_val, then_block, else_block)

        self.generator.builder.position_at_end(then_block)
        self.generate_block_statement(node.then_block)
        if not self.generator.builder.block.is_terminated:
            self.generator.builder.branch(merge_block)

        self.generator.builder.position_at_end(else_block)
        if node.else_block:
            self.generate_block_statement(node.else_block)
        if not self.generator.builder.block.is_terminated:
            self.generator.builder.branch(merge_block)

        self.generator.builder.position_at_end(merge_block)

    def generate_echo_statement(self, node: EchoStatement) -> None:
        value = self.generator.generate_expression(node.expression)
        val_type = value.type

        if val_type == IRType.bool():
            specifier = self.generator.module.globals["fstr_bool"]
            cast_value = self.generator.builder.zext(value, IRType.int(32))
        elif val_type == IRType.int(32):
            specifier = self.generator.module.globals["fstr_int"]
            cast_value = value
        elif val_type == IRType.float():
            specifier = self.generator.module.globals["fstr_float"]
            cast_value = value
        elif isinstance(val_type, ir.PointerType) and val_type.pointee == IRType.int(8):
            specifier = self.generator.module.globals["fstr_str"]
            cast_value = value
        else:
            raise TypeError(f"Unsupported type: {val_type}")

        fmt_ptr = self.generator.builder.bitcast(specifier, IRType.char().as_pointer())

        printf_func = self.generator.module.globals["printf"]
        fflush_func = self.generator.module.globals["fflush"]

        self.generator.builder.call(printf_func, [fmt_ptr, cast_value])
        self.generator.builder.call(fflush_func, [NullPointerConst])
