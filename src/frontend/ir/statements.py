# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownArgumentType=false
# pyright: reportOptionalMemberAccess=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false

from llvmlite import ir
from frontend.ir.components.loop import LoopGenerator
from frontend.ir.helpers import get_ir_type
from frontend.ir.types import IRType, NullPointerConst
from frontend.ir.typing import IRGeneratorABC, StatementGeneratorABC
from frontend.syntax.ast import *
from frontend.syntax.ast import WhileStatement


class StatementGenerator(StatementGeneratorABC):
    """The StatementGenerator generates LLVM intermediate representation (IR)
    code for statements in the AST. It traverses the AST and generates IR for
    each statement node."""

    def __init__(self, generator: IRGeneratorABC):
        self.generator = generator
        self.loop_generator = LoopGenerator(generator)

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
        return self.loop_generator.generate_while_statement(node)

    def generate_each_statement(self, node: EachStatement) -> None:
        return self.loop_generator.generate_each_statement(node)

    def generate_range_statement(self, node: RangeStatement) -> None:
        return self.loop_generator.generate_range_statement(node)

    def generate_halt_statement(self, _node: HaltStatement) -> None:
        return self.loop_generator.generate_halt_statement(_node)

    def generate_skip_statement(self, _node: SkipStatement) -> None:
        return self.loop_generator.generate_skip_statement(_node)

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
