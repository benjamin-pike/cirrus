from typing import *
from lexer.tokens import TokenType

class VarType: ...

class PrimitiveType(VarType):
    def __init__(self, primitive: TokenType):
        self.primitive = primitive
    def __repr__(self):
        return f'PrimitiveType({self.primitive})'
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, PrimitiveType) and self.primitive == other.primitive
    def __hash__(self) -> int:
        return hash(self.__repr__())

class InferType(PrimitiveType):
    def __init__(self):
        super().__init__(TokenType.INFER)

class VoidType(PrimitiveType):
    def __init__(self):
        super().__init__(TokenType.VOID)

class ArrayType(VarType):
    def __init__(self, element_type: VarType):
        self.element_type = element_type
    def __repr__(self):
        return f'ArrayType({self.element_type})'
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ArrayType) and self.element_type == other.element_type
    def __hash__(self) -> int:
        return hash(self.__repr__())

class FunctionType(VarType):
    def __init__(self, return_type: VarType, param_types: List[Tuple[str, VarType]]):
        self.return_type = return_type
        self.param_types = param_types
    def __repr__(self):
        return f'Function({self.return_type}, {self.param_types})'
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, FunctionType) and self.return_type == other.return_type and self.param_types == other.param_types
    def __hash__(self) -> int:
        return hash(self.__repr__())
