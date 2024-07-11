# pyright: reportArgumentType=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false

from llvmlite import ir
from frontend.ir.helpers import get_ir_type
from frontend.ir.types import IRType
from frontend.ir.typing import ArrayGeneratorABC, IRGeneratorABC
from frontend.syntax.ast import *


class ArrayGenerator(ArrayGeneratorABC):
    """Generates LLVM IR for array literals and associated methods."""

    def __init__(self, generator: IRGeneratorABC):
        self.generator = generator

    def generate_array_literal(self, node: ArrayLiteral) -> ir.Value:
        """Generate LLVM IR for an array literal.

        Args:
            node (ArrayLiteral): The array literal node

        Returns:
            ir.Value: The LLVM IR value (pointer to array struct)
        """
        assert isinstance(node.type, ArrayType)
        element_type = get_ir_type(node.type.element_type)

        array_struct_type = ir.LiteralStructType(
            [
                IRType.int(32),  # size
                IRType.int(32),  # capacity
                element_type.as_pointer(),  # data pointer to element_type
            ]
        )

        # Allocate the array structure
        array_struct_ptr = self.generator.builder.alloca(array_struct_type)

        self._initialize_array_size_and_capacity(array_struct_ptr, len(node.elements))

        # Heap allocate array data using malloc
        element_size = element_type.get_abi_size(self.generator.target_data)
        malloc_func = self.generator.module.get_global("malloc")
        initial_capacity = max(4, len(node.elements))
        total_size = self.generator.builder.mul(
            ir.Constant(IRType.int(32), initial_capacity),
            ir.Constant(IRType.int(32), element_size),
        )
        data_array_ptr = self.generator.builder.bitcast(
            self.generator.builder.call(malloc_func, [total_size]),
            element_type.as_pointer(),
        )

        # Initialize array data
        for i, element in enumerate(node.elements):
            element_ptr = self.generator.builder.gep(
                data_array_ptr, [ir.Constant(IRType.int(32), i)]
            )
            self.generator.builder.store(
                self.generator.generate_expression(element), element_ptr
            )

        self._store_data_pointer(array_struct_ptr, data_array_ptr)

        return array_struct_ptr

    def generate_index_expression(self, node: IndexExpression) -> ir.Value:
        """Generate LLVM IR for an index expression.

        Args:
            node (IndexExpression): The index expression node

        Returns:
            ir.Value: The LLVM IR value of the indexed element
        """
        array_struct_ptr = self.generator.generate_expression(node.array)
        index = self.generator.generate_expression(node.index)

        data_field_ptr = self.generator.builder.gep(
            array_struct_ptr,
            [ir.Constant(IRType.int(32), 0), ir.Constant(IRType.int(32), 2)],
        )
        data_ptr = self.generator.builder.load(data_field_ptr)

        element_ptr = self.generator.builder.gep(data_ptr, [index])

        return self.generator.builder.load(element_ptr)

    def generate_array_method_call(self, node: MethodCallExpression) -> ir.Value:
        """Generate LLVM IR for an array method call.

        Args:
            node (MethodCallExpression): The method call expression node

        Returns:
            ir.Value: The LLVM IR value of the method call result
        """
        array = self.generator.generate_expression(node.composite)
        method = node.method.name

        match method:
            case "push":
                return self._generate_array_push(array, *node.args)
            case "pop":
                return self._generate_array_pop(array)
            case "insert":
                return self._generate_array_insert(array, *node.args)
            case "extract":
                return self._generate_array_extract(array, *node.args)
            case _:
                raise NotImplementedError(f"Array method '{method}' not implemented")

    # Array Methods
    def _generate_array_push(
        self, array_struct_ptr: ir.Value, element: Expression
    ) -> ir.Value:
        size_ptr, capacity_ptr, data_ptr = self._load_array_fields(array_struct_ptr)

        size = self.generator.builder.load(size_ptr)
        capacity = self.generator.builder.load(capacity_ptr)
        data_ptr_val = self.generator.builder.load(data_ptr)

        self._reallocate_if_full(size, capacity, data_ptr_val, capacity_ptr, data_ptr)

        data_ptr_val = self.generator.builder.load(data_ptr)
        element_val = self.generator.generate_expression(element)

        new_size = self.generator.builder.add(size, ir.Constant(IRType.int(32), 1))
        self.generator.builder.store(new_size, size_ptr)
        new_element_ptr = self.generator.builder.gep(data_ptr_val, [size])
        self.generator.builder.store(element_val, new_element_ptr)

        return array_struct_ptr

    def _generate_array_pop(self, array_struct_ptr: ir.Value) -> ir.Value:
        size_ptr, _, data_ptr = self._load_array_fields(array_struct_ptr)

        size = self.generator.builder.load(size_ptr)
        data_ptr_val = self.generator.builder.load(data_ptr)

        self._validate_not_empty(size)

        new_size = self.generator.builder.sub(size, ir.Constant(IRType.int(32), 1))
        last_element_ptr = self.generator.builder.gep(data_ptr_val, [new_size])
        last_element_val = self.generator.builder.load(last_element_ptr)

        self.generator.builder.store(new_size, size_ptr)

        return last_element_val

    def _generate_array_insert(
        self, array_struct_ptr: ir.Value, index: Expression, element: Expression
    ) -> ir.Value:
        size_ptr, capacity_ptr, data_ptr = self._load_array_fields(array_struct_ptr)

        size = self.generator.builder.load(size_ptr)
        capacity = self.generator.builder.load(capacity_ptr)
        data_ptr_val = self.generator.builder.load(data_ptr)

        index_val = self.generator.generate_expression(index)
        element_val = self.generator.generate_expression(element)

        # Check array bounds
        self._validate_index_bounds(index_val, size)
        self._reallocate_if_full(size, capacity, data_ptr_val, capacity_ptr, data_ptr)

        data_ptr_val = self.generator.builder.load(data_ptr)

        # Shift elements to the right
        self._shift_elements(data_ptr_val, size, index_val, "right")

        insert_ptr = self.generator.builder.gep(data_ptr_val, [index_val])
        self.generator.builder.store(element_val, insert_ptr)

        new_size = self.generator.builder.add(size, ir.Constant(IRType.int(32), 1))
        self.generator.builder.store(new_size, size_ptr)

        return array_struct_ptr

    def _generate_array_extract(
        self, array_struct_ptr: ir.Value, index: Expression
    ) -> ir.Value:
        """Generate LLVM IR for the array extract method.

        Args:
            array_struct_ptr (ir.Value): The pointer to the array structure
            index (Expression): The index to extract the element

        Returns:
            ir.Value: The LLVM IR value of the extracted element
        """
        size_ptr, _, data_ptr = self._load_array_fields(array_struct_ptr)

        size = self.generator.builder.load(size_ptr)
        data_ptr_val = self.generator.builder.load(data_ptr)

        index_val = self.generator.generate_expression(index)

        # Check if the index is within bounds
        self._validate_index_bounds(index_val, size)

        # Retrieve the element
        element_ptr = self.generator.builder.gep(data_ptr_val, [index_val])
        element_val = self.generator.builder.load(element_ptr)

        # Shift elements to the left
        self._shift_elements(data_ptr_val, size, index_val, "left")

        new_size = self.generator.builder.sub(size, ir.Constant(IRType.int(32), 1))
        self.generator.builder.store(new_size, size_ptr)

        return element_val

    # Helpers
    def _initialize_array_size_and_capacity(
        self, array_struct_ptr: ir.Value, initial_size: int
    ):
        size_ptr = self.generator.builder.gep(
            array_struct_ptr,
            [ir.Constant(IRType.int(32), 0), ir.Constant(IRType.int(32), 0)],
        )
        self.generator.builder.store(
            ir.Constant(IRType.int(32), initial_size), size_ptr
        )

        capacity_ptr = self.generator.builder.gep(
            array_struct_ptr,
            [ir.Constant(IRType.int(32), 0), ir.Constant(IRType.int(32), 1)],
        )
        initial_capacity = max(4, initial_size)
        self.generator.builder.store(
            ir.Constant(IRType.int(32), initial_capacity), capacity_ptr
        )

    def _store_data_pointer(self, array_struct_ptr: ir.Value, data_array_ptr: ir.Value):
        data_ptr = self.generator.builder.bitcast(data_array_ptr, data_array_ptr.type)
        data_field_ptr = self.generator.builder.gep(
            array_struct_ptr,
            [ir.Constant(IRType.int(32), 0), ir.Constant(IRType.int(32), 2)],
        )
        self.generator.builder.store(data_ptr, data_field_ptr)

    def _load_array_fields(self, array_struct_ptr: ir.Value):
        size_ptr = self.generator.builder.gep(
            array_struct_ptr,
            [ir.Constant(IRType.int(32), 0), ir.Constant(IRType.int(32), 0)],
        )
        capacity_ptr = self.generator.builder.gep(
            array_struct_ptr,
            [ir.Constant(IRType.int(32), 0), ir.Constant(IRType.int(32), 1)],
        )
        data_field_ptr = self.generator.builder.gep(
            array_struct_ptr,
            [ir.Constant(IRType.int(32), 0), ir.Constant(IRType.int(32), 2)],
        )
        return size_ptr, capacity_ptr, data_field_ptr

    def _validate_index_bounds(self, index_val: ir.Value, size: ir.Value):
        is_out_of_bounds = self.generator.builder.icmp_signed(">", index_val, size)
        error_block = self.generator.builder.append_basic_block()
        continue_block = self.generator.builder.append_basic_block()
        self.generator.builder.cbranch(is_out_of_bounds, error_block, continue_block)

        # Error handling block
        self.generator.builder.position_at_end(error_block)
        self.generator.builder.call(
            self.generator.module.get_global("exit"), [ir.Constant(IRType.int(32), 1)]
        )
        self.generator.builder.unreachable()

        # Continue block
        self.generator.builder.position_at_end(continue_block)

    def _validate_not_empty(self, size: ir.Value):
        is_empty = self.generator.builder.icmp_signed(
            "==", size, ir.Constant(IRType.int(32), 0)
        )

        # Create basic blocks for conditional branching
        error_block = self.generator.builder.append_basic_block()
        continue_block = self.generator.builder.append_basic_block()

        # Branch according to the result of is_empty
        self.generator.builder.cbranch(is_empty, error_block, continue_block)

        # Error handling block
        self.generator.builder.position_at_end(error_block)
        self.generator.builder.call(
            self.generator.module.get_global("exit"), [ir.Constant(IRType.int(32), 1)]
        )
        self.generator.builder.unreachable()

        # Continue block
        self.generator.builder.position_at_end(continue_block)

    def _reallocate_if_full(
        self,
        size: ir.Value,
        capacity: ir.Value,
        data_ptr: ir.Value,
        capacity_ptr: ir.Value,
        data_field_ptr: ir.Value,
    ):
        is_full = self.generator.builder.icmp_signed("==", size, capacity)
        with self.generator.builder.if_then(is_full):
            data_ptr_casted = self.generator.builder.bitcast(
                data_ptr, IRType.int(8).as_pointer()
            )
            element_type = data_ptr.type.pointee
            element_size = element_type.get_abi_size(self.generator.target_data)
            new_capacity = self.generator.builder.mul(
                capacity, ir.Constant(IRType.int(32), 2)
            )
            new_capacity_bytes = self.generator.builder.mul(
                new_capacity, ir.Constant(IRType.int(32), element_size)
            )
            realloc_func = self.generator.module.get_global("realloc")
            new_data_ptr_casted = self.generator.builder.call(
                realloc_func,
                [data_ptr_casted, new_capacity_bytes],
            )
            new_data_ptr = self.generator.builder.bitcast(
                new_data_ptr_casted, data_ptr.type
            )
            self.generator.builder.store(new_capacity, capacity_ptr)
            self.generator.builder.store(new_data_ptr, data_field_ptr)

    def _shift_elements(
        self, data_ptr: ir.Value, size: ir.Value, index_val: ir.Value, direction: str
    ):
        loop_entry_block = self.generator.builder.append_basic_block()
        self.generator.builder.branch(loop_entry_block)
        self.generator.builder.position_at_end(loop_entry_block)

        loop_index = self.generator.builder.alloca(IRType.int(32))
        if direction == "right":
            self.generator.builder.store(size, loop_index)
        else:
            self.generator.builder.store(index_val, loop_index)

        loop_cond_block = self.generator.builder.append_basic_block()
        loop_body_block = self.generator.builder.append_basic_block()
        loop_end_block = self.generator.builder.append_basic_block()

        self.generator.builder.branch(loop_cond_block)
        self.generator.builder.position_at_end(loop_cond_block)

        loop_index_val = self.generator.builder.load(loop_index)
        if direction == "right":
            loop_cond = self.generator.builder.icmp_signed(
                ">", loop_index_val, index_val
            )
        else:
            loop_cond = self.generator.builder.icmp_signed(
                "<",
                loop_index_val,
                self.generator.builder.sub(size, ir.Constant(IRType.int(32), 1)),
            )

        self.generator.builder.cbranch(loop_cond, loop_body_block, loop_end_block)

        self.generator.builder.position_at_end(loop_body_block)

        current_ptr = self.generator.builder.gep(data_ptr, [loop_index_val])
        if direction == "right":
            next_index_val = self.generator.builder.sub(
                loop_index_val, ir.Constant(IRType.int(32), 1)
            )
        else:
            next_index_val = self.generator.builder.add(
                loop_index_val, ir.Constant(IRType.int(32), 1)
            )
        next_ptr = self.generator.builder.gep(data_ptr, [next_index_val])
        self.generator.builder.store(self.generator.builder.load(next_ptr), current_ptr)

        self.generator.builder.store(next_index_val, loop_index)
        self.generator.builder.branch(loop_cond_block)

        self.generator.builder.position_at_end(loop_end_block)
