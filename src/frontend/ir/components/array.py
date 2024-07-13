# pyright: reportReturnType=false
# pyright: reportArgumentType=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownParameterType=false

from llvmlite import ir
from frontend.ir.helpers import get_ir_type
from frontend.ir.types import IRType
from frontend.ir.typing import ArrayGeneratorABC, IRGeneratorABC
from frontend.syntax.ast import *


class ArrayGenerator(ArrayGeneratorABC):
    """Generates LLVM IR for array literals and associated methods."""

    def __init__(self, generator: IRGeneratorABC):
        self.generator = generator

        self.arrpush = self._define_arrpush()
        self.arrpop = self._define_arrpop()
        self.arrinsert = self._define_arrinsert()
        self.arrextract = self._define_arrextract()

    def generate_array_literal(self, node: ArrayLiteral) -> ir.Value:
        assert isinstance(node.type, ArrayType)

        element_type = get_ir_type(node.type.element_type)
        array_struct_type = IRType.array(element_type)

        # Stack allocate space for the array
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

    # Array method implementations
    def _generate_array_push(
        self, array_struct_ptr: ir.Value, element: Expression
    ) -> ir.Value:
        element_val = self.generator.generate_expression(element)
        element_size = element_val.type.get_abi_size(self.generator.target_data)
        element_ptr = self.generator.builder.alloca(element_val.type)
        self.generator.builder.store(element_val, element_ptr)

        # Cast to generic pointers
        array_struct_ptr_cast = self.generator.builder.bitcast(
            array_struct_ptr, IRType.array(IRType.int(8)).as_pointer()
        )
        element_ptr_cast = self.generator.builder.bitcast(
            element_ptr, ir.PointerType(ir.IntType(8))
        )

        # Call the arrpush function
        self.generator.builder.call(
            self.arrpush,
            [
                array_struct_ptr_cast,
                element_ptr_cast,
                ir.Constant(ir.IntType(32), element_size),
            ],
        )

        return array_struct_ptr

    def _generate_array_pop(self, array_struct_ptr: ir.Value) -> ir.Value:
        data_ptr = self.generator.builder.gep(
            array_struct_ptr,
            [ir.Constant(IRType.int(32), 0), ir.Constant(IRType.int(32), 2)],
        ).type.pointee

        element_size = data_ptr.pointee.get_abi_size(self.generator.target_data)
        array_struct_ptr_cast = self.generator.builder.bitcast(
            array_struct_ptr, IRType.array(IRType.int(8)).as_pointer()
        )

        popped_element_ptr = self.generator.builder.alloca(data_ptr.pointee)
        popped_element_ptr_cast = self.generator.builder.bitcast(
            popped_element_ptr, ir.PointerType(ir.IntType(8))
        )

        self.generator.builder.call(
            self.arrpop,
            [
                array_struct_ptr_cast,
                popped_element_ptr_cast,
                ir.Constant(ir.IntType(32), element_size),
            ],
        )

        return self.generator.builder.load(popped_element_ptr)

    def _generate_array_insert(
        self, array_struct_ptr: ir.Value, index: Expression, element: Expression
    ) -> ir.Value:
        element_val = self.generator.generate_expression(element)
        element_ptr = self.generator.builder.alloca(element_val.type)
        self.generator.builder.store(element_val, element_ptr)

        # Cast to generic pointers
        array_struct_ptr_cast = self.generator.builder.bitcast(
            array_struct_ptr, IRType.array(IRType.int(8)).as_pointer()
        )
        element_ptr_cast = self.generator.builder.bitcast(
            element_ptr, ir.PointerType(ir.IntType(8))
        )

        index_val = self.generator.generate_expression(index)

        self.generator.builder.call(
            self.arrinsert,
            [
                array_struct_ptr_cast,
                index_val,
                element_ptr_cast,
                ir.Constant(
                    ir.IntType(32),
                    element_val.type.get_abi_size(self.generator.target_data),
                ),
            ],
        )

        return array_struct_ptr

    def _generate_array_extract(
        self, array_struct_ptr: ir.Value, index: Expression
    ) -> ir.Value:
        data_ptr = self.generator.builder.gep(
            array_struct_ptr,
            [ir.Constant(IRType.int(32), 0), ir.Constant(IRType.int(32), 2)],
        ).type.pointee

        element_size = data_ptr.pointee.get_abi_size(self.generator.target_data)
        array_struct_ptr_cast = self.generator.builder.bitcast(
            array_struct_ptr, IRType.array(IRType.int(8)).as_pointer()
        )

        extracted_element_ptr = self.generator.builder.alloca(data_ptr.pointee)
        extracted_element_ptr_cast = self.generator.builder.bitcast(
            extracted_element_ptr, ir.PointerType(ir.IntType(8))
        )

        self.generator.builder.call(
            self.arrextract,
            [
                array_struct_ptr_cast,
                self.generator.generate_expression(index),
                extracted_element_ptr_cast,
                ir.Constant(ir.IntType(32), element_size),
            ],
        )

        return self.generator.builder.load(extracted_element_ptr)

    # Array method definitions
    def _define_arrpush(self):
        func = ir.Function(
            self.generator.module,
            ir.FunctionType(
                IRType.void(),
                [
                    IRType.array(IRType.int(8)).as_pointer(),  # Array pointer (generic)
                    IRType.pointer(IRType.int(8)),  # Element pointer (generic)
                    IRType.int(32),  # Element size (bytes)
                ],
            ),
            "arrpush",
        )

        self.generator.enter_function(func)

        array_struct_ptr, element_ptr, element_size = func.args

        # Load array fields
        size_ptr, capacity_ptr, data_field_ptr = self._load_array_fields(
            array_struct_ptr
        )

        size = self.generator.builder.load(size_ptr)
        capacity = self.generator.builder.load(capacity_ptr)
        data_ptr = self.generator.builder.load(data_field_ptr)

        # Reallocate the array if full
        self._reallocate_if_full(
            size, capacity, data_ptr, capacity_ptr, data_field_ptr, element_size
        )

        data_ptr = self.generator.builder.load(data_field_ptr)

        # Calculate the new element position and increase the size
        new_size = self.generator.builder.add(size, ir.Constant(ir.IntType(32), 1))
        self.generator.builder.store(new_size, size_ptr)
        element_position = self.generator.builder.mul(size, element_size)
        new_element_ptr = self.generator.builder.gep(data_ptr, [element_position])

        # Use memcpy to copy the element data
        self.generator.builder.call(
            self.generator.module.get_global("memcpy"),
            [new_element_ptr, element_ptr, element_size, ir.Constant(ir.IntType(1), 0)],
        )

        self.generator.builder.ret_void()
        self.generator.exit_function()

        return func

    def _define_arrpop(self):
        func = ir.Function(
            self.generator.module,
            ir.FunctionType(
                IRType.void(),
                [
                    IRType.array(IRType.int(8)).as_pointer(),  # Array pointer (generic)
                    IRType.pointer(
                        IRType.int(8)
                    ),  # Popped element allocation (generic)
                    IRType.int(32),  # Element size (bytes)
                ],
            ),
            "arrpop",
        )
        self.generator.enter_function(func)

        array_struct_ptr, popped_element_alloc, element_size = func.args

        # Load array fields
        size_ptr, _, data_field_ptr = self._load_array_fields(array_struct_ptr)

        size = self.generator.builder.load(size_ptr)
        data_ptr = self.generator.builder.load(data_field_ptr)

        # Validate that the array is not empty
        self._validate_not_empty(size)

        # Get the last element
        new_size = self.generator.builder.sub(size, ir.Constant(ir.IntType(32), 1))
        self.generator.builder.store(new_size, size_ptr)
        last_element_offset = self.generator.builder.mul(new_size, element_size)
        last_element_ptr = self.generator.builder.gep(data_ptr, [last_element_offset])

        # Copy the last element to the popped element allocation
        self.generator.builder.call(
            self.generator.module.get_global("memcpy"),
            [
                popped_element_alloc,
                last_element_ptr,
                element_size,
                ir.Constant(ir.IntType(1), 0),
            ],
        )

        self.generator.builder.ret_void()
        self.generator.exit_function()

        return func

    def _define_arrinsert(self):
        func = ir.Function(
            self.generator.module,
            ir.FunctionType(
                IRType.void(),
                [
                    IRType.array(IRType.int(8)).as_pointer(),  # Array pointer (generic)
                    IRType.int(32),  # Index
                    IRType.pointer(None),  # Element pointer (generic)
                    IRType.int(32),  # Element size (bytes)
                ],
            ),
            "arrinsert",
        )
        self.generator.enter_function(func)

        array_struct_ptr, index, element_ptr, element_size = func.args

        # Load array fields
        size_ptr, capacity_ptr, data_field_ptr = self._load_array_fields(
            array_struct_ptr
        )

        size = self.generator.builder.load(size_ptr)
        capacity = self.generator.builder.load(capacity_ptr)
        data_ptr = self.generator.builder.load(data_field_ptr)

        # Reallocate if full
        self._reallocate_if_full(
            size, capacity, data_ptr, capacity_ptr, data_field_ptr, element_size
        )

        data_ptr = self.generator.builder.load(data_field_ptr)

        # Validate the index
        self._validate_index_bounds(index, size)

        # Shift elements after the target index to the right
        self._shift_elements(data_ptr, size, index, element_size, "right")

        # Resize the array and calculate the insertion position
        new_size = self.generator.builder.add(size, ir.Constant(ir.IntType(32), 1))
        self.generator.builder.store(new_size, size_ptr)
        element_offset = self.generator.builder.mul(index, element_size)
        new_element_ptr = self.generator.builder.gep(data_ptr, [element_offset])

        # Use memcpy to copy the element data
        self.generator.builder.call(
            self.generator.module.get_global("memcpy"),
            [new_element_ptr, element_ptr, element_size, ir.Constant(ir.IntType(1), 0)],
        )

        self.generator.builder.ret_void()
        self.generator.exit_function()

        return func

    def _define_arrextract(self):
        func = ir.Function(
            self.generator.module,
            ir.FunctionType(
                IRType.void(),
                [
                    IRType.array(IRType.int(8)).as_pointer(),  # Array pointer (generic)
                    IRType.int(32),  # Index,
                    IRType.pointer(None),  # Extracted element pointer (generic)
                    IRType.int(32),  # Element size (bytes)
                ],
            ),
            "arrextract",
        )
        self.generator.enter_function(func)

        array_struct_ptr, index, extracted_element_alloc, element_size = func.args

        # Load array fields
        size_ptr, _, data_field_ptr = self._load_array_fields(array_struct_ptr)
        size = self.generator.builder.load(size_ptr)
        data_ptr = self.generator.builder.load(data_field_ptr)

        # Validate the index
        self._validate_index_bounds(index, size)

        # Find the target element and reduce the size of the array
        element_offest = self.generator.builder.mul(index, element_size)
        element_ptr = self.generator.builder.gep(data_ptr, [element_offest])
        new_size = self.generator.builder.sub(size, ir.Constant(IRType.int(32), 1))
        self.generator.builder.store(new_size, size_ptr)

        self.generator.builder.call(
            self.generator.module.get_global("memcpy"),
            [
                extracted_element_alloc,
                element_ptr,
                element_size,
                ir.Constant(ir.IntType(1), 0),
            ],
        )

        # Shift elements after target index to the left
        self._shift_elements(data_ptr, size, index, element_size, "left")

        self.generator.builder.ret_void()
        self.generator.exit_function()
        return func

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

    def _validate_index_bounds(self, index_val: ir.Value, arr_size: ir.Value):
        is_out_of_bounds = self.generator.builder.icmp_signed(">", index_val, arr_size)
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
        element_size: ir.Value,
    ):
        is_full = self.generator.builder.icmp_signed("==", size, capacity)
        with self.generator.builder.if_then(is_full):
            data_ptr_casted = self.generator.builder.bitcast(
                data_ptr, IRType.pointer(None)
            )
            # element_type = data_ptr.type.pointee
            # element_size = element_type.get_abi_size(self.generator.target_data)
            new_capacity = self.generator.builder.mul(
                capacity, ir.Constant(IRType.int(32), 2)
            )
            new_capacity_bytes = self.generator.builder.mul(new_capacity, element_size)
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
        self,
        data_ptr: ir.Value,
        size: ir.Value,
        index_val: ir.Value,
        element_size: ir.Value,
        direction: str,
    ):
        if direction not in ("left", "right"):
            raise ValueError("Invalid direction")

        loop_entry_block = self.generator.builder.append_basic_block()
        self.generator.builder.branch(loop_entry_block)
        self.generator.builder.position_at_end(loop_entry_block)

        loop_index = self.generator.builder.alloca(IRType.int(32))
        match direction:
            case "left":
                self.generator.builder.store(index_val, loop_index)
            case "right":
                self.generator.builder.store(size, loop_index)

        loop_cond_block = self.generator.builder.append_basic_block()
        loop_body_block = self.generator.builder.append_basic_block()
        loop_end_block = self.generator.builder.append_basic_block()

        self.generator.builder.branch(loop_cond_block)
        self.generator.builder.position_at_end(loop_cond_block)

        loop_index_val = self.generator.builder.load(loop_index)
        match direction:
            case "left":
                loop_cond = self.generator.builder.icmp_signed(
                    "<",
                    loop_index_val,
                    self.generator.builder.sub(size, ir.Constant(IRType.int(32), 1)),
                )
            case "right":
                loop_cond = self.generator.builder.icmp_signed(
                    ">", loop_index_val, index_val
                )

        self.generator.builder.cbranch(loop_cond, loop_body_block, loop_end_block)
        self.generator.builder.position_at_end(loop_body_block)

        match direction:
            case "left":
                next_index_val = self.generator.builder.add(
                    loop_index_val, ir.Constant(IRType.int(32), 1)
                )
            case "right":
                next_index_val = self.generator.builder.sub(
                    loop_index_val, ir.Constant(IRType.int(32), 1)
                )

        self.generator.builder.call(
            self.generator.module.get_global("memcpy"),
            [
                self.generator.builder.gep(
                    data_ptr, [self.generator.builder.mul(loop_index_val, element_size)]
                ),
                self.generator.builder.gep(
                    data_ptr, [self.generator.builder.mul(next_index_val, element_size)]
                ),
                element_size,
                ir.Constant(ir.IntType(1), 0),
            ],
        )

        self.generator.builder.store(next_index_val, loop_index)
        self.generator.builder.branch(loop_cond_block)

        self.generator.builder.position_at_end(loop_end_block)
