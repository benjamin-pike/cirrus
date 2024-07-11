from typing import *
from frontend.semantic.types import *
from frontend.semantic.typing import ScopeABC, SymbolABC, SymbolTableABC
from frontend.syntax.ast import *


class Symbol(SymbolABC):
    """Represents a symbol in the symbol table."""

    def __init__(self, name: str, var_type: VarType) -> None:
        self.name = name
        self.var_type = var_type

    def __repr__(self) -> str:
        return f"Symbol(name={self.name}, var_type={self.var_type})"


class Scope(ScopeABC):
    """Represents a scope in the symbol table."""

    def __init__(self, parent_node: Optional[Node] = None) -> None:
        self.symbols: Dict[str, SymbolABC] = {}
        self.parent_node = parent_node
        self.reachable = True

    def __repr__(self) -> str:
        return (
            f"Scope(parent_node={self.parent_node}, "
            f"symbols={self.symbols}, reachable={self.reachable})"
        )


class SymbolTable(SymbolTableABC):
    """Represents a symbol table for managing variables and functions."""

    def __init__(self) -> None:
        self.scopes: List[ScopeABC] = [Scope()]

    def enter_scope(self, parent_node: Optional[Node] = None) -> None:
        self.scopes.append(Scope(parent_node))

    def exit_scope(self) -> None:
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            raise IndexError("Cannot exit the global scope")

    def define(self, name: str, var_type: VarType) -> None:
        current_scope = self.scopes[-1]
        if name in current_scope.symbols:
            raise KeyError(f"Symbol {name} already declared in the current scope")
        current_scope.symbols[name] = Symbol(name, var_type)

    def lookup(self, name: str, limit_to_function: bool = False) -> Optional[SymbolABC]:
        for scope in reversed(self.scopes):
            if name in scope.symbols:
                return scope.symbols[name]
            if limit_to_function and isinstance(scope.parent_node, FunctionDeclaration):
                break

        return None

    def get_scope(self, symbol: SymbolABC) -> Optional[ScopeABC]:
        for scope in reversed(self.scopes):
            if symbol in scope.symbols.values():
                return scope

        return None

    def get_current_function_type(self) -> Optional[FunctionType]:
        for scope in reversed(self.scopes):
            if isinstance(scope.parent_node, FunctionDeclaration):
                return scope.parent_node.function_type
            if isinstance(scope.parent_node, FunctionLiteral):
                return FunctionType(InferType(), scope.parent_node.parameters)

        return None

    def is_loop_scope(self) -> bool:
        for scope in reversed(self.scopes):
            if scope.parent_node and isinstance(scope.parent_node, FunctionDeclaration):
                return False
            if scope.parent_node and isinstance(
                scope.parent_node, (WhileStatement, RangeStatement, EachStatement)
            ):
                return True

        return False

    def is_reachable(self) -> bool:
        for scope in reversed(self.scopes):
            if not scope.reachable:
                return False

        return True

    def set_unreachable(self) -> None:
        self.scopes[-1].reachable = False
