from typing import *
from semantic.types import FunctionType, VarType
from semantic.typing import ScopeABC, SymbolABC, SymbolTableABC
from syntax.ast import EachStatement, FunctionDeclaration, RangeStatement, Statement, WhileStatement

class Symbol(SymbolABC):
    """
    Represents a symbol in the symbol table.

    Attributes:
        name (str): The name of the symbol.
        var_type (VarType): The type of the symbol.
    """
    def __init__(self, name: str, var_type: VarType) -> None:
        self.name = name
        self.var_type = var_type

    def __repr__(self) -> str:
        return f'Symbol(name={self.name}, var_type={self.var_type})'

class Scope(ScopeABC):
    """
    Represents a scope in the symbol table.

    Attributes:
        symbols (Dict[str, Symbol]): A dictionary mapping names to symbols.
        function_type (Optional[FunctionType]): The function type if this scope is a function scope, otherwise None.
    """
    def __init__(self, parent_node: Optional[Statement] = None) -> None:
        self.symbols: Dict[str, SymbolABC] = {}
        self.parent_node = parent_node
        self.reachable = True

    def __repr__(self) -> str:
        return f'Scope(parent_node={self.parent_node}, symbols={list(self.symbols.keys())})'

class SymbolTable(SymbolTableABC):
    """
    Represents a symbol table for managing variables and functions.

    Attributes:
        scopes (List[Scope]): A stack of scopes.
    """
    def __init__(self) -> None:
        """Initializes the symbol table with an empty global scope."""
        self.scopes: List[ScopeABC] = [Scope()]

    def enter_scope(self, parent_node: Optional[Statement] = None) -> None:
        """Enters a new scope, optionally as a function scope.

        Args:
            parent_node (Optional[Statement]): The parent node of the scope.
        """
        self.scopes.append(Scope(parent_node))

    def exit_scope(self) -> None:
        """Exits the current scope by popping it off the scope stack.

        Raises:
            IndexError: If attempting to exit the global scope.
        """
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            raise IndexError('Cannot exit the global scope')

    def define(self, name: str, var_type: VarType) -> None:
        """Adds a symbol to the current scope.

        Args:
            name (str): The name of the symbol.
            var_type (VarType): The type of the symbol.

        Raises:
            KeyError: If the symbol is already declared in the current scope.
        """
        current_scope = self.scopes[-1]
        if name in current_scope.symbols:
            raise KeyError(f'Symbol {name} already declared in the current scope')
        current_scope.symbols[name] = Symbol(name, var_type)

    def lookup(self, name: str, limit_to_function: bool = False) -> Optional[SymbolABC]:
        """Looks up a symbol by name, starting from the innermost scope.

        Args:
            name (str): The name of the symbol to lookup.
            limit_to_function (bool): If True, only search up to the nearest function scope.

        Returns:
            Optional[Symbol]: The symbol if found, otherwise None.
        """
        for scope in reversed(self.scopes):
            if name in scope.symbols:
                return scope.symbols[name]
            if limit_to_function and isinstance(scope.parent_node, FunctionDeclaration):
                break

    def get_scope(self, symbol: SymbolABC) -> Optional[ScopeABC]:
        """Gets the scope containing the given symbol.

        Args:
            symbol (Symbol): The symbol to look up.

        Returns:
            Optional[Scope]: The scope containing the symbol if found, otherwise None.
        """
        for scope in reversed(self.scopes):
            if symbol in scope.symbols.values():
                return scope

    def get_current_function_type(self) -> Optional[FunctionType]:
        """Gets the function type of the current function scope, if any.

        Returns:
            Optional[FunctionType]: The function type if in a function, otherwise None.
        """
        for scope in reversed(self.scopes):
            if isinstance(scope.parent_node, FunctionDeclaration):
                return scope.parent_node.function_type

    def is_loop_scope(self) -> bool:
        """ Checks if the current scope is within a loop.

        Returns:
            bool: True if the current scope is within a loop, otherwise False.
        """

        for scope in reversed(self.scopes):
            if scope.parent_node and isinstance(scope.parent_node, FunctionDeclaration):
                return False
            if scope.parent_node and isinstance(scope.parent_node, (WhileStatement, RangeStatement, EachStatement)):
                return True

        return False

    def is_reachable(self) -> bool:
        """ Checks if the current scope is reachable.

        Returns:
            bool: True if the current scope is reachable, otherwise False.
        """

        for scope in reversed(self.scopes):
            if not scope.reachable:
                return False

        return True

    def set_unreachable(self) -> None:
        """ Marks the current scope as unreachable.
        """

        self.scopes[-1].reachable = False
