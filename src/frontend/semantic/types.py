from abc import ABC
from typing import Any, List, Tuple, Dict
from frontend.lexer.tokens import TokenType


class VarType(ABC):
    """Abstract class for all types"""


class PrimitiveType(VarType):
    """Represents primitive types

    Args:
        primitive (TokenType): The primitive type
    """

    def __init__(self, primitive: TokenType):
        self.primitive = primitive

    def __repr__(self):
        return f"PrimitiveType({self.primitive.name})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, PrimitiveType) and self.primitive == other.primitive

    def __hash__(self) -> int:
        return hash(self.__repr__())


class InferType(PrimitiveType):
    """Represents the infer type"""

    def __init__(self):
        super().__init__(TokenType.INFER)


class VoidType(PrimitiveType):
    """Represents the void type"""

    def __init__(self):
        super().__init__(TokenType.VOID)


class FunctionType(VarType):
    """Represents function types

    Args:
        return_type (VarType): The return type of the function
        param_types (List[Tuple[str, VarType]]): The parameter types of the function
    """

    def __init__(self, return_type: VarType, param_types: List[Tuple[str, VarType]]):
        self.return_type = return_type
        self.param_types = param_types

    def __repr__(self):
        return f"Function({self.return_type}, {self.param_types})"

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, FunctionType)
            and self.return_type == other.return_type
            and self.param_types == other.param_types
        )

    def __hash__(self) -> int:
        return hash(self.__repr__())


class ArrayType(VarType):
    """Represents array types

    Args:
        element_type (VarType): The type of the elements in the array
    """

    def __init__(self, element_type: VarType):
        self.element_type = element_type

    def __repr__(self):
        return f"ArrayType({self.element_type})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ArrayType) and (
            (self.element_type == other.element_type)
            or (self.element_type == VoidType() or other.element_type == VoidType())
        )

    def __hash__(self) -> int:
        return hash(self.__repr__())


class SetType(VarType):
    """Represents set types

    Args:
        element_type (VarType): The type of the elements in the set
    """

    def __init__(self, element_type: VarType):
        self.element_type = element_type
        self.attributes = {}
        self.methods = {
            "add": FunctionType(self, [("element", element_type)]),
            "remove": FunctionType(self, [("element", element_type)]),
            "clear": FunctionType(self, []),
            "contains": FunctionType(
                PrimitiveType(TokenType.BOOL), [("element", element_type)]
            ),
            "size": FunctionType(PrimitiveType(TokenType.INT), []),
        }

    def __repr__(self):
        return f"SetType({self.element_type})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, SetType) and (
            (self.element_type == other.element_type)
            or (self.element_type == VoidType() or other.element_type == VoidType())
        )

    def __hash__(self) -> int:
        return hash(self.__repr__())


class MapType(VarType):
    """Represents map types

    Args:
        key_type (VarType): The type of the keys in the map
    """

    def __init__(self, key_type: VarType, value_type: VarType):
        self.key_type = key_type
        self.value_type = value_type
        self.attributes = {}
        self.methods = {
            "get": FunctionType(value_type, [("key", key_type)]),
            "put": FunctionType(self, [("key", key_type), ("value", value_type)]),
            "remove": FunctionType(self, [("key", key_type)]),
            "clear": FunctionType(self, []),
            "contains": FunctionType(
                PrimitiveType(TokenType.BOOL), [("key", key_type)]
            ),
            "size": FunctionType(PrimitiveType(TokenType.INT), []),
        }

    def __repr__(self):
        return f"MapType({self.key_type}, {self.value_type})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, MapType) and (
            (self.key_type == other.key_type and self.value_type == other.value_type)
            or (
                (self.key_type == VoidType() and self.value_type == VoidType())
                or (other.key_type == VoidType() and other.value_type == VoidType())
            )
        )

    def __hash__(self) -> int:
        return hash(self.__repr__())


class CustomTypeIdentifier(VarType):
    """Represents template identifiers

    Args:
        name (str): The name of the template
    """

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"CustomTypeIdentifier({self.name})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TemplateType):
            return self.name == other.identifier.name

        return isinstance(other, CustomTypeIdentifier) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.__repr__())


class TemplateType(VarType):
    """Represents template types

    Args:
        attributes (List[Tuple[str, VarType]]): The attributes of the template
        methods (Dict[str, FunctionType]): The methods of the template
    """

    def __init__(
        self,
        identifier: CustomTypeIdentifier,
        attributes: Dict[str, VarType],
        methods: Dict[str, FunctionType],
    ):
        self.identifier = identifier
        self.attributes = attributes
        self.methods = methods

    def __repr__(self):
        return f"TemplateType({self.identifier}, {self.attributes}, {self.methods})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, CustomTypeIdentifier):
            return self.identifier.name == other.name

        if isinstance(other, TemplateType):
            attributes_match = all(
                a == b
                for a, b in zip(self.attributes.items(), other.attributes.items())
            )
            methods_match = all(
                a == b for a, b in zip(self.methods.items(), other.methods.items())
            )
            return attributes_match and methods_match

        return False

    def __hash__(self) -> int:
        return hash(self.__repr__())
