from typing import *
import re

def pascal_to_snake_case(name: str) -> str:
    """Converts a PascalCase string to snake_case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

def is_iterable(obj: Any) -> bool:
    """Returns True if the object is an iterable."""
    return hasattr(obj, '__iter__')
