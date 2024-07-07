from typing import Union

from llvmlite import ir
from frontend.ir.types import IRType
from frontend.lexer.tokens import TokenType
from frontend.semantic.types import ArrayType, FunctionType, PrimitiveType, VarType


def get_ir_type(var_type: Union[VarType, None]) -> ir.Type:
    """Get the corresponding IR type for a given VarType.

    Args:
        var_type (Union[VarType, None]): The VarType to get the IR type for.

    Returns:
        ir.Type: The corresponding IR type.
    """

    if not var_type:
        raise ValueError("Node type not defined.")

    if isinstance(var_type, PrimitiveType):
        match var_type.primitive:
            case TokenType.INT:
                return IRType.int(32)
            case TokenType.FLOAT:
                return IRType.float()
            case TokenType.BOOL:
                return IRType.bool()
            case TokenType.STR:
                return IRType.char().as_pointer()
            case TokenType.VOID:
                return IRType.void()
            case TokenType.NULL:
                return IRType.null()
            case _:
                raise NotImplementedError(
                    f"IR generation for '{var_type.primitive}' not implemented."
                )
    if isinstance(var_type, ArrayType):
        return ir.ArrayType(
            get_ir_type(var_type.element_type), var_type.size
        ).as_pointer()
    if isinstance(var_type, FunctionType):
        return ir.FunctionType(
            get_ir_type(var_type.return_type),
            [get_ir_type(param[1]) for param in var_type.param_types],
        ).as_pointer()

    raise NotImplementedError(
        f"IR type generation for {type(var_type).__name__} not implemented."
    )
