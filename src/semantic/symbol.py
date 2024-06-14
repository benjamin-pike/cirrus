from typing import *
from semantic.types import FunctionType, VarType

class Symbol:
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

class Scope:
    """
    Represents a scope in the symbol table.

    Attributes:
        symbols (Dict[str, Symbol]): A dictionary mapping names to symbols.
        function_type (Optional[FunctionType]): The function type if this scope is a function scope, otherwise None.
    """
    def __init__(self, function_type: Optional[FunctionType] = None) -> None:
        self.symbols: Dict[str, Symbol] = {}
        self.function_type = function_type

    def __repr__(self) -> str:
        return f'Scope(function_type={self.function_type}, symbols={list(self.symbols.keys())})'

class SymbolTable:
    """
    Represents a symbol table for managing variables and functions.

    Attributes:
        scopes (List[Scope]): A stack of scopes.
    """
    def __init__(self) -> None:
        """Initializes the symbol table with an empty global scope."""
        self.scopes: List[Scope] = [Scope()]

    def enter_scope(self, function_type: Optional[FunctionType] = None) -> None:
        """Enters a new scope, optionally as a function scope.

        Args:
            function_type (Optional[FunctionType]): If provided, the new scope is a function scope with the given function type.
        """
        self.scopes.append(Scope(function_type))

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

    def lookup(self, name: str, limit_to_function: bool = False) -> Optional[Symbol]:
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
            if limit_to_function and scope.function_type is not None:
                break

        return

    def get_scope(self, symbol: Symbol) -> Optional[Scope]:
        """Gets the scope containing the given symbol.

        Args:
            symbol (Symbol): The symbol to look up.

        Returns:
            Optional[Scope]: The scope containing the symbol if found, otherwise None.
        """
        for scope in reversed(self.scopes):
            if symbol in scope.symbols.values():
                return scope

        return

    def get_current_function_scope(self) -> Optional[Scope]:
        """Gets the function type of the current function scope, if any.

        Returns:
            Optional[FunctionType]: The function type if in a function, otherwise None.
        """
        for scope in reversed(self.scopes):
            if scope.function_type is not None:
                return scope

        return
