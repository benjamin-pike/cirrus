# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownArgumentType=false
# pyright: reportOptionalMemberAccess=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false

from llvmlite import ir
from frontend.ir.types import IRType
from frontend.ir.typing import IRGeneratorABC
from frontend.syntax.ast import *


class LoopGenerator:
    """Generate LLVM IR for loop constructs (while, each, and range)."""

    _loop_stack = []

    def __init__(self, generator: IRGeneratorABC):
        self.generator = generator

    # Loops
    def generate_while_statement(self, node: WhileStatement) -> None:
        """Generate LLVM IR for a while statement.

        Args:
            node (WhileStatement): The while statement node
        """
        # Generate loop blocks, append them to loop stack and branch to condition block
        cond_block, body_block, _, end_block = self._configure_loop()

        # Check if the condition is true and branch to the body else branch to the end
        self.generator.builder.position_at_end(cond_block)
        cond_val = self.generator.generate_expression(node.condition)
        self.generator.builder.cbranch(cond_val, body_block, end_block)

        # Generate the body and branch back to the condition block
        self.generator.builder.position_at_end(body_block)
        self.generator.generate_statement(node.body)
        self.generator.builder.branch(cond_block)

        self._finalize_loop(end_block)

    def generate_each_statement(self, node: EachStatement) -> None:
        """Generate LLVM IR for an each statement.

        Args:
            node (EachStatement): The each statement node
        """
        # Allocate memory for the index variable and initialize it to 0
        index_ptr = self.generator.builder.alloca(IRType.int(32))
        self.generator.builder.store(ir.Constant(IRType.int(32), 0), index_ptr)

        # Get the array length and data pointer from the array struct
        array_struct_ptr = self.generator.generate_expression(node.iterable)
        size_ptr = self.generator.builder.gep(
            array_struct_ptr,
            [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)],
        )
        data_field_ptr = self.generator.builder.gep(
            array_struct_ptr,
            [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 2)],
        )
        array_length = self.generator.builder.load(size_ptr)
        data_ptr = self.generator.builder.load(data_field_ptr)

        # Generate loop blocks, append them to loop stack and branch to condition block
        cond_block, body_block, next_block, end_block = self._configure_loop(True)

        # Check if the index is less than the array length and branch to the body
        self.generator.builder.position_at_end(cond_block)
        index_val = self.generator.builder.load(index_ptr)
        cond = self.generator.builder.icmp_signed("<", index_val, array_length)
        self.generator.builder.cbranch(cond, body_block, end_block)

        # Set the loop variable to the current element and generate body
        self.generator.builder.position_at_end(body_block)
        self.generator.symbol_table[node.variable] = self.generator.builder.gep(
            data_ptr, [index_val]
        )
        self.generator.generate_statement(node.body)
        self.generator.builder.branch(next_block)

        # Increment the index and branch back to the condition block
        self.generator.builder.position_at_end(next_block)
        next_idx = self.generator.builder.add(index_val, ir.Constant(IRType.int(32), 1))
        self.generator.builder.store(next_idx, index_ptr)
        self.generator.builder.branch(cond_block)

        self._finalize_loop(end_block)

    def generate_range_statement(self, node: RangeStatement) -> None:
        """Generate LLVM IR for a range statement.

        Args:
            node (RangeStatement): The range statement node
        """
        # Allocate memory for the loop variable and initialize it to the start value
        loop_var_ptr = self.generator.builder.alloca(IRType.int(32))
        start_val = self.generator.generate_expression(node.start)
        self.generator.builder.store(start_val, loop_var_ptr)

        # Generate basic blocks for the loop
        cond_block, body_block, next_block, end_block = self._configure_loop(True)

        # Check if the loop variable is less than the end value and branch to the body
        self.generator.builder.position_at_end(cond_block)
        loop_var_val = self.generator.builder.load(loop_var_ptr)
        end_val = self.generator.generate_expression(node.end)
        cond = self.generator.builder.icmp_signed("<", loop_var_val, end_val)
        self.generator.builder.cbranch(cond, body_block, end_block)

        # Set the loop variable to the current value and generate the body
        self.generator.builder.position_at_end(body_block)
        self.generator.symbol_table[node.identifier] = loop_var_ptr
        self.generator.generate_statement(node.body)
        self.generator.builder.branch(next_block)

        # Increment the loop variable and branch back to the condition block
        self.generator.builder.position_at_end(next_block)
        increment_val = self.generator.generate_expression(node.increment)
        next_val = self.generator.builder.add(loop_var_val, increment_val)
        self.generator.builder.store(next_val, loop_var_ptr)
        self.generator.builder.branch(cond_block)

        self._finalize_loop(end_block)

    # Control flow statements
    def generate_halt_statement(self, _node: HaltStatement) -> None:
        """Generate LLVM IR for a halt statement.

        Args:
            _node (HaltStatement): The halt statement node
        """
        _, _, end_block = self._loop_stack[-1]
        self.generator.builder.branch(end_block)

    def generate_skip_statement(self, _node: SkipStatement) -> None:
        """Generate LLVM IR for a skip statement.

        Args:
            _node (SkipStatement): The skip statement node
        """
        cond_block, next_block, _ = self._loop_stack[-1]
        self.generator.builder.branch(next_block if next_block else cond_block)

    # Helper methods
    def _configure_loop(self, has_next: bool = False):
        """Generate loop blocks, append to loop stack, and branch to condition block."""
        cond_block = self.generator.func.append_basic_block()
        body_block = self.generator.func.append_basic_block()
        next_block = self.generator.func.append_basic_block() if has_next else None
        end_block = self.generator.func.append_basic_block()

        self._loop_stack.append((cond_block, next_block, end_block))
        self.generator.builder.branch(cond_block)

        return cond_block, body_block, next_block, end_block

    def _finalize_loop(self, end_block: ir.Block):
        """Pop the loop stack and set the builder position to the end block."""
        self._loop_stack.pop()
        self.generator.builder.position_at_end(end_block)
