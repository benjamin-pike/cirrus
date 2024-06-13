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

class SymbolTable:
    """
    Represents a symbol table for managing variables and functions.

    Attributes:
        scopes (List[Dict[str, Symbol]]): A stack of scopes, each a dictionary mapping names to symbols.
    """
    def __init__(self) -> None:
        """ Initializes the symbol table with an empty global scope. """
        self.scopes: List[Dict[str, Symbol]] = [{}]

        self.function_types: List[FunctionType] = []
        self.function_scopes: List[Dict[str, Symbol]] = [{}]

    def enter_scope(self) -> None:
        """ Enters a new scope by pushing a new dictionary onto the scope stack. """
        self.scopes.append({})

    def enter_function_scope(self, fn_type: FunctionType) -> None:
        self.enter_scope()

        self.function_scopes.append(self.scopes[-1])
        self.function_types.append(fn_type)

    def exit_scope(self) -> None:
        """ Exits the current scope by popping the dictionary off the scope stack. """
        self.scopes.pop()

    def exit_function_scope(self) -> None:
        self.exit_scope() # Also pops the function scope as the memory address is shared
        self.function_types.pop()

    def define(self, name: str, var_type: VarType) -> None:
        """ Adds a symbol to the current scope.

        Args:
            name (str): The name of the symbol.
            var_type (VarType): The type of the symbol.

        Raises:
            KeyError: If the symbol is already declared in the current scope.
        """
        if name in self.scopes[-1]:
            raise KeyError(f'Symbol {name} already declared in the current scope')
        self.scopes[-1][name] = Symbol(name, var_type)

    def lookup(self, name: str) -> Optional[Symbol]:
        """ Looks up a symbol by name, starting from the innermost scope.

        Args:
            name (str): The name of the symbol to lookup.

        Returns:
            Optional[Symbol]: The symbol if found, otherwise None.
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def get_current_function_scope(self) -> Optional[Dict[str, Symbol]]:
        if not self.function_scopes:
            return None

        return self.function_scopes[-1]

    def get_current_function_type(self) -> Optional[FunctionType]:
        if not self.function_types:
            return None

        return self.function_types[-1]
