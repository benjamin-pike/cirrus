from typing import *
from lexer.tokens import TokenType

class VarType(): ...

class PrimitiveType(VarType):
    def __init__(self, primitive: TokenType):
        self.primitive = primitive
    def __repr__ (self):
        return f'{self.primitive}'

class ArrayType(VarType):
    def __init__(self, element_type: VarType):
        self.element_type = element_type
    def __repr__ (self):
        return f'Array({self.element_type})'
