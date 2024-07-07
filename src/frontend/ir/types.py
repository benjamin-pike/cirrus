from typing import cast
from llvmlite import ir


class IRTypeGenerator:
    """Provides methods for creating typesafe LLVM IR types."""

    def int(self, size: int) -> ir.IntType:
        """Returns an LLVM IR integer type of the specified size.

        Args:
            size: The size of the integer type in bits.
        """
        if size not in [1, 8, 16, 32, 64]:
            raise ValueError(f"Invalid integer size: {size}")
        return cast(ir.IntType, ir.IntType(size))

    def float(self) -> ir.FloatType:
        """Returns an LLVM IR floating-point type."""
        return ir.FloatType()

    def bool(self) -> ir.IntType:
        """Returns an LLVM IR boolean type."""
        return self.int(1)

    def char(self) -> ir.IntType:
        """Returns an LLVM IR character type."""
        return self.int(8)

    def void(self) -> ir.VoidType:
        """Returns an LLVM IR void type."""
        return ir.VoidType()

    def null(self) -> ir.PointerType:
        """Returns an LLVM IR null type."""
        return self.int(8).as_pointer()

    def pointer(self, pointee_type: ir.Type) -> ir.PointerType:
        """Returns an LLVM IR pointer type."""
        return ir.PointerType(pointee_type)


IRType = IRTypeGenerator()

NullPointerConst = ir.Constant(IRType.null(), None)
