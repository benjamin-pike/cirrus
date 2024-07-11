# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownMemberType=false

from llvmlite import ir, binding as llvm

from frontend.ir.expressions import ExpressionGenerator
from frontend.ir.statements import StatementGenerator
from frontend.ir.typing import IRGeneratorABC
from frontend.ir.types import *
from frontend.syntax.ast import Expression, Program, Statement
from lib.helpers import pascal_to_snake_case


class IRGenerator(IRGeneratorABC):
    """The IRGenerator class generates LLVM intermediate representation (IR) code
    from an AST. It traverses the AST and generates IR for each node in the AST."""

    symbol_table = {}

    def __init__(self):
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        self.module = ir.Module()
        self.module.triple = llvm.get_default_triple()
        self.target_data = llvm.create_target_data(self.module.data_layout)

        self.func = ir.Function(self.module, ir.FunctionType(IRType.void(), []), "main")
        self.builder = ir.IRBuilder(self.func.append_basic_block())

        self.statement_generator = StatementGenerator(self)
        self.expression_generator = ExpressionGenerator(self)

        # Auxillary functions
        self._declare_printf()
        self._declare_fmt_specifiers()
        self._declare_c_str_funcs()
        self._declare_c_memory_funcs()
        self._declare_c_exit()

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
        return getattr(self.statement_generator, method_name)(node)

    def generate_expression(self, node: Expression) -> ir.Value:
        """Generate LLVM IR for an expression.

        Args:
            node (Expression): The expression node

        Returns:
            ir.Value: The LLVM IR value representing the expression
        """
        method_name = f"generate_{pascal_to_snake_case(type(node).__name__)}"
        return getattr(self.expression_generator, method_name)(node)

    # C Functions
    def _declare_printf(self) -> None:
        """Declare the printf and fflush functions in the LLVM module."""

        voidptr_ty = IRType.int(8).as_pointer()
        printf_ty = ir.FunctionType(IRType.int(32), [voidptr_ty], var_arg=True)
        ir.Function(self.module, printf_ty, name="printf")

        fflush_ty = ir.FunctionType(IRType.int(32), [voidptr_ty])
        ir.Function(self.module, fflush_ty, name="fflush")

    def _declare_c_str_funcs(self) -> None:
        """Declare C string functions in the LLVM module."""
        void_ptr = IRType.int(8).as_pointer()
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
        malloc_ty = ir.FunctionType(IRType.int(8).as_pointer(), [IRType.int(32)])
        ir.Function(self.module, malloc_ty, name="malloc")

        realloc_ty = ir.FunctionType(
            IRType.int(8).as_pointer(), [IRType.int(8).as_pointer(), IRType.int(32)]
        )
        ir.Function(self.module, realloc_ty, name="realloc")

    def _declare_c_exit(self) -> None:
        """Declare the exit function in the LLVM module."""
        exit_ty = ir.FunctionType(IRType.void(), [IRType.int(32)])
        ir.Function(self.module, exit_ty, name="exit")
