# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownMemberType=false

from llvmlite import ir, binding as llvm

from frontend.ir.components.array import ArrayGenerator
from frontend.ir.components.loop import LoopGenerator
from frontend.ir.components.string import StringGenerator
from frontend.ir.expressions import ExpressionGenerator
from frontend.ir.statements import StatementGenerator
from frontend.ir.typing import IRGeneratorABC
from frontend.ir.types import *
from frontend.syntax.ast import Expression, Program, Statement
from lib.helpers import pascal_to_snake_case


class IRGenerator(IRGeneratorABC):
    """Generates LLVM intermediate representation (IR) code from an AST."""

    symbol_table = {}

    def __init__(self):
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        self.module = ir.Module()
        self.module.triple = llvm.get_default_triple()
        self.target_data = llvm.create_target_data(self.module.data_layout)

        self.func = ir.Function(self.module, ir.FunctionType(IRType.void(), []), "main")
        self.block = self.func.append_basic_block()
        self.builder = ir.IRBuilder(self.block)

        self.func_stack = [
            {
                "func": self.func,
                "block": self.block,
                "builder": self.builder,
            }
        ]

        # Auxillary functions
        self._declare_printf()
        self._declare_fmt_specifiers()
        self._declare_c_str_funcs()
        self._declare_c_memory_funcs()
        self._declare_c_exit()

        # Generators
        self.expression_generator = ExpressionGenerator(self)
        self.statement_generator = StatementGenerator(self)

        # Specific Generators
        self.array_generator = ArrayGenerator(self)
        self.string_generator = StringGenerator(self)
        self.loop_generator = LoopGenerator(self)

    def generate_program(self, node: Program) -> ir.Module:
        """Generate LLVM IR for a program.

        Args:
            node (Program): The program node

        Returns:
            ir.Module: The LLVM IR module representing the program
        """
        for statement in node.body:
            self.generate_statement(statement)
        self.builder.ret_void()

        return self.module

    def generate_statement(self, node: Statement) -> ir.Module:
        """Generate LLVM IR for a statement.

        Args:
            node (Statement): The statement node

        Returns:
            ir.Value: The LLVM IR value representing the statement
        """
        method_name = f"generate_{pascal_to_snake_case(type(node).__name__)}"

        if hasattr(self.loop_generator, method_name):
            return getattr(self.loop_generator, method_name)(node)

        return getattr(self.statement_generator, method_name)(node)

    def generate_expression(self, node: Expression) -> ir.Value:
        """Generate LLVM IR for an expression.

        Args:
            node (Expression): The expression node

        Returns:
            ir.Value: The LLVM IR value representing the expression
        """
        method_name = f"generate_{pascal_to_snake_case(type(node).__name__)}"

        if hasattr(self.string_generator, method_name):
            return getattr(self.string_generator, method_name)(node)
        if hasattr(self.array_generator, method_name):
            return getattr(self.array_generator, method_name)(node)

        return getattr(self.expression_generator, method_name)(node)

    # Function stack management
    def enter_function(self, func: ir.Function) -> None:
        """Enter a new function scope."""

        entry = func.append_basic_block()

        self.func = func
        self.block = entry
        self.builder = ir.IRBuilder(entry)

        self.func_stack.append(
            {"func": func, "block": self.block, "builder": self.builder}
        )

    def exit_function(self) -> None:
        """Exit the current function scope."""
        self.func_stack.pop()

        self.func = self.func_stack[-1]["func"]
        self.block = self.func_stack[-1]["block"]
        self.builder = self.func_stack[-1]["builder"]

    # C Functions
    def _declare_printf(self) -> None:
        """Declare the printf and fflush functions in the LLVM module."""

        voidptr_ty = IRType.pointer(None)
        printf_ty = ir.FunctionType(IRType.int(32), [voidptr_ty], var_arg=True)
        ir.Function(self.module, printf_ty, name="printf")

        fflush_ty = ir.FunctionType(IRType.int(32), [voidptr_ty])
        ir.Function(self.module, fflush_ty, name="fflush")

    def _declare_c_str_funcs(self) -> None:
        """Declare C string functions in the LLVM module."""
        void_ptr = IRType.pointer(None)
        char_ptr = IRType.char().as_pointer()

        strcmp_ty = ir.FunctionType(IRType.int(32), [void_ptr, void_ptr], var_arg=False)
        ir.Function(self.module, strcmp_ty, name="strcmp")

        strlen_ty = ir.FunctionType(IRType.int(32), [void_ptr], var_arg=False)
        ir.Function(self.module, strlen_ty, name="strlen")

        strcpy_ty = ir.FunctionType(char_ptr, [void_ptr, void_ptr], var_arg=False)
        ir.Function(self.module, strcpy_ty, name="strcpy")

        strcat_ty = ir.FunctionType(char_ptr, [void_ptr, void_ptr], var_arg=False)
        ir.Function(self.module, strcat_ty, name="strcat")

    def _declare_fmt_specifiers(self) -> None:
        """Declare format specifier strings for printf in the LLVM module."""
        specifiers = {
            "int": "%d\n\0",
            "float": "%f\n\0",
            "str": "%s\n\0",
            "bool": "%d\n\0",
        }

        for ty, specifier in specifiers.items():
            format_str_bytes = bytearray(specifier.encode("utf8"))
            c_format_str = ir.Constant(
                ir.ArrayType(IRType.int(8), len(format_str_bytes)), format_str_bytes
            )

            global_format_str = ir.GlobalVariable(
                self.module, c_format_str.type, name=f"fstr_{ty}"
            )
            global_format_str.linkage = "internal"
            global_format_str.global_constant = True
            global_format_str.initializer = c_format_str

    def _declare_c_memory_funcs(self) -> None:
        """Declare C memory functions in the LLVM module."""
        malloc_ty = ir.FunctionType(IRType.pointer(None), [IRType.int(32)])
        ir.Function(self.module, malloc_ty, name="malloc")

        realloc_ty = ir.FunctionType(
            IRType.pointer(None), [IRType.pointer(None), IRType.int(32)]
        )
        ir.Function(self.module, realloc_ty, name="realloc")

        memcpy_ty = ir.FunctionType(
            IRType.pointer(None),
            [
                IRType.pointer(None),
                IRType.pointer(None),
                IRType.int(32),
                IRType.int(1),
            ],
        )
        ir.Function(self.module, memcpy_ty, name="memcpy")

    def _declare_c_exit(self) -> None:
        """Declare the exit function in the LLVM module."""
        exit_ty = ir.FunctionType(IRType.void(), [IRType.int(32)])
        ir.Function(self.module, exit_ty, name="exit")
