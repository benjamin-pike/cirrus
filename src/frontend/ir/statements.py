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
    """The StatementGenerator generates LLVM intermediate representation (IR)
    code for statements in the AST. It traverses the AST and generates IR for
    each statement node."""

    def __init__(self, generator: IRGeneratorABC):
        self.generator = generator

    def generate_expression_statement(self, node: ExpressionStatement) -> None:
        """Generate LLVM IR for an expression statement.

        Args:
            node (ExpressionStatement): The expression statement node
        """
        self.generator.generate_expression(node.expression)

    def generate_variable_declaration(self, node: VariableDeclaration) -> None:
        """Generate LLVM IR for a variable declaration.

        Args:
            node (VariableDeclaration): The variable declaration node
        """
        var_type = get_ir_type(node.var_type)
        initializer = self.generator.generate_expression(node.initializer)
        var_ptr = self.generator.builder.alloca(var_type, name=node.name)

        self.generator.builder.store(initializer, var_ptr)
        self.generator.symbol_table[node.name] = var_ptr

    def generate_function_declaration(self, node: FunctionDeclaration) -> None:
        """Generate LLVM IR for a function declaration.

        Args:
            node (FunctionDeclaration): The function declaration node
        """
        parent = self.generator.builder

        func_type = get_ir_type(node.function_type)
        func = ir.Function(self.generator.module, func_type.pointee, node.name)

        entry = func.append_basic_block("entry")
        self.generator.builder = ir.IRBuilder(entry)
        self.generator.func = func
        self.generator.block = entry
        self.generator.symbol_table[node.name] = func

        for i, (param_name, _) in enumerate(node.function_type.param_types):
            arg = func.args[i]
            arg_ptr = self.generator.builder.alloca(arg.type, name=param_name)
            self.generator.builder.store(arg, arg_ptr)
            self.generator.symbol_table[param_name] = arg_ptr

        self.generator.generate_statement(node.body)

        self.generator.builder = parent

    def generate_return_statement(self, node: ReturnStatement) -> None:
        """Generate LLVM IR for a return statement.

        Args:
            node (ReturnStatement): The return statement node
        """
        if node.expression is None:
            self.generator.builder.ret_void()
            return

        retval = self.generator.generate_expression(node.expression)
        self.generator.builder.ret(retval)

    def generate_block_statement(self, node: BlockStatement) -> None:
        """Generate LLVM IR for a block statement.

        Args:
            node (BlockStatement): The block statement node
        """
        for statement in node.statements:
            self.generator.generate_statement(statement)

    def generate_if_statement(self, node: IfStatement) -> None:
        """Generate LLVM IR for an if statement.

        Args:
            node (IfStatement): The if statement node
        """
        cond_val = self.generator.generate_expression(node.condition)
        then_block = self.generator.func.append_basic_block(name="if.then")
        else_block = self.generator.func.append_basic_block(name="if.else")
        merge_block = self.generator.func.append_basic_block(name="if.merge")

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

    def generate_while_statement(self, node: WhileStatement) -> None:
        """Generate LLVM IR for a while statement.

        Args:
            node (WhileStatement): The while statement node
        """
        loop_cond_block = self.generator.func.append_basic_block(name="while.cond")
        loop_body_block = self.generator.func.append_basic_block(name="while.body")
        loop_end_block = self.generator.func.append_basic_block(name="while.end")

        self.generator.builder.branch(loop_cond_block)

        self.generator.builder.position_at_end(loop_cond_block)
        cond_val = self.generator.generate_expression(node.condition)
        self.generator.builder.cbranch(cond_val, loop_body_block, loop_end_block)

        self.generator.builder.position_at_end(loop_body_block)
        self.generate_block_statement(node.body)
        self.generator.builder.branch(loop_cond_block)

        self.generator.builder.position_at_end(loop_end_block)

    def generate_each_statement(self, node: EachStatement) -> None:
        """Generate LLVM IR for an each statement.

        Args:
            node (EachStatement): The each statement node
        """
        loop_entry_block = self.generator.func.append_basic_block(name="each.entry")
        self.generator.builder.branch(loop_entry_block)
        self.generator.builder.position_at_end(loop_entry_block)

        index_var = self.generator.builder.alloca(IRType.int(32), name="index")
        self.generator.builder.store(ir.Constant(IRType.int(32), 0), index_var)

        array_ptr = self.generator.generate_expression(node.iterable)
        array_length = ir.Constant(IRType.int(32), array_ptr.type.pointee.count)

        loop_cond_block = self.generator.func.append_basic_block(name="each.cond")
        self.generator.builder.branch(loop_cond_block)
        self.generator.builder.position_at_end(loop_cond_block)

        index_val = self.generator.builder.load(index_var, name="index_val")
        cond = self.generator.builder.icmp_signed(
            "<", index_val, array_length, name="loop_cond"
        )

        loop_body_block = self.generator.func.append_basic_block(name="each.body")
        loop_end_block = self.generator.func.append_basic_block(name="each.end")

        self.generator.builder.cbranch(cond, loop_body_block, loop_end_block)

        self.generator.builder.position_at_end(loop_body_block)

        element_ptr = self.generator.builder.gep(
            array_ptr, [ir.Constant(IRType.int(32), 0), index_val]
        )

        self.generator.symbol_table[node.variable] = element_ptr

        self.generate_block_statement(node.body)

        next_index = self.generator.builder.add(
            index_val, ir.Constant(IRType.int(32), 1), name="next_index"
        )

        self.generator.builder.store(next_index, index_var)
        self.generator.builder.branch(loop_cond_block)
        self.generator.builder.position_at_end(loop_end_block)

    def generate_range_statement(self, node: RangeStatement) -> None:
        """Generate LLVM IR for a range statement.

        Args:
            node (RangeStatement): The range statement node
        """
        loop_entry_block = self.generator.func.append_basic_block(name="range.entry")
        self.generator.builder.branch(loop_entry_block)
        self.generator.builder.position_at_end(loop_entry_block)

        loop_var = self.generator.builder.alloca(IRType.int(32), name=node.identifier)
        start_val = self.generator.generate_expression(node.start)
        self.generator.builder.store(start_val, loop_var)

        loop_cond_block = self.generator.func.append_basic_block(name="range.cond")
        self.generator.builder.branch(loop_cond_block)
        self.generator.builder.position_at_end(loop_cond_block)

        loop_var_val = self.generator.builder.load(
            loop_var, name=f"{node.identifier}_val"
        )
        end_val = self.generator.generate_expression(node.end)
        cond = self.generator.builder.icmp_signed(
            "<", loop_var_val, end_val, name="loop_cond"
        )

        loop_body_block = self.generator.func.append_basic_block(name="range.body")
        loop_end_block = self.generator.func.append_basic_block(name="range.end")

        self.generator.builder.cbranch(cond, loop_body_block, loop_end_block)

        self.generator.builder.position_at_end(loop_body_block)

        self.generator.symbol_table[node.identifier] = loop_var
        self.generate_block_statement(node.body)

        increment_val = self.generator.generate_expression(node.increment)
        next_val = self.generator.builder.add(
            loop_var_val, increment_val, name=f"{node.identifier}_next"
        )
        self.generator.builder.store(next_val, loop_var)

        self.generator.builder.branch(loop_cond_block)

        self.generator.builder.position_at_end(loop_end_block)

    def generate_echo_statement(self, node: EchoStatement) -> None:
        """Generate LLVM IR for an echo statement.

        Args:
            node (EchoStatement): The echo statement node
        """
        value = self.generator.generate_expression(node.expression)
        value_type = value.type

        if value_type == IRType.bool():
            specifier = self.generator.module.globals["fstr_bool"]
            cast_value = self.generator.builder.zext(value, IRType.int(32))
        elif value_type == IRType.int(32):
            specifier = self.generator.module.globals["fstr_int"]
            cast_value = value
        elif value_type == IRType.float():
            specifier = self.generator.module.globals["fstr_float"]
            cast_value = value
        elif isinstance(
            value_type, ir.PointerType
        ) and value_type.pointee == IRType.int(8):
            specifier = self.generator.module.globals["fstr_str"]
            cast_value = value
        else:
            raise TypeError(f"Unsupported type: {value_type}")

        fmt_ptr = self.generator.builder.bitcast(specifier, IRType.char().as_pointer())

        printf_func = self.generator.module.globals["printf"]
        fflush_func = self.generator.module.globals["fflush"]

        self.generator.builder.call(printf_func, [fmt_ptr, cast_value])
        self.generator.builder.call(fflush_func, [NullPointerConst])
