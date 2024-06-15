from typing import *
from lexer.tokens import TokenType
from semantic.types import FunctionType, VarType

class Node(): ...
class Statement(Node): ...
class Expression(Node): ...

# Program
class Program(Node):
    def __init__(self, body: List[Statement]) -> None:
        self.body: List[Statement] = body
    def __repr__(self) -> str:
        return f'Program({self.body})'

# Statements
class VariableDeclaration(Statement):
    """ Node representing a variable declaration statement.

    Syntax:
        let <variable_name> = <initializer>;

    Example:
        let x = 5;
    """
    def __init__(self, name: str, var_type: VarType, initializer: Node) -> None:
        self.name = name
        self.var_type = var_type
        self.initializer = initializer
    def __repr__(self) -> str:
        return f'VariableDeclaration({self.name}, {self.var_type}, {self.initializer})'

class ExpressionStatement(Statement):
    """ Node representing an expression statement.

    Args:
        expression (Node): The expression to be evaluated.

    Syntax:
        <expression>;

    Example:
        5 + 5;
    """
    def __init__(self, expression: Node) -> None:
        self.expression = expression
    def __repr__(self) -> str:
        return f'ExpressionStatement({self.expression})'

class BlockStatement(Statement):
    """ Node representing a block statement.

    Args:
        statements (List[Statement]): The statements within the block.

    Syntax:
        { <statements> }

    Example:
        {
            let x = 5;
            let y = 10;
        }
    """
    def __init__(self, statements: List[Statement]) -> None:
        self.statements = statements

    def __repr__(self) -> str:
        return f'BlockStatement({self.statements})'

class IfStatement(Statement):
    """ Node representing an if statement.

    Args:
        condition (Expression): The condition to be evaluated.
        then_block (BlockStatement): The block to be executed if the condition is true.
        else_block (Optional[BlockStatement]): The block to be executed if the condition is false.

    Syntax:
        if <condition> <then_block> else <else_block>

    Example:
        if x > 5 {
            return x;
        } else {
            return 5;
        }
    """
    def __init__(self, condition: Expression, then_block: BlockStatement, else_block: Optional[BlockStatement]) -> None:
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def __repr__(self) -> str:
        return f'IfStatement({self.condition}, {self.then_block}, {self.else_block})'

class WhileStatement(Statement):
    """ Node representing a while statement.

    Args:
        condition (Expression): The condition to be evaluated.
        body (BlockStatement): The block to be executed while the condition is true.

    Syntax:
        while <condition> <body>

    Example:
        while x < 5 {
            x = x + 1;
        }
    """

    def __init__(self, condition: Expression, body: BlockStatement) -> None:
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f'WhileStatement({self.condition}, {self.body})'

class RangeStatement(Statement):
    """ Node representing a range statement.

    Args:
        identifier (str): The identifier to be used in the range.
        start (Expression): The starting value of the range.
        end (Expression): The ending value of the range.
        increment (Expression): The increment value of the range.
        body (BlockStatement): The block to be executed for each value in the range.

    Syntax:
        range <identifier> in <start> to <end> by <increment> <body>

    Example:
        range i in 0 to 10 by 1 {
            echo i;
        }
    """
    def __init__(self, identifier: str, start: Expression, end: Expression, increment: Expression, body: BlockStatement) -> None:
        self.identifier = identifier
        self.start = start
        self.end = end
        self.increment = increment
        self.body = body

    def __repr__(self) -> str:
        return f'RangeStatement({self.identifier}, {self.start}, {self.end}, {self.increment}, {self.body})'

class EachStatement(Statement):
    """ Node representing an each statement.

    Args:
        variable (str): The variable to be used in the each statement.
        iterable (Expression): The iterable to be looped over.
        body (BlockStatement): The block to be executed for each value in the iterable.

    Syntax:
        each <variable> in <iterable> <body>

    Example:
        each item in items {
            echo item;
        }
    """
    def __init__(self, variable: str, iterable: Expression, body: BlockStatement) -> None:
        self.variable = variable
        self.iterable = iterable
        self.body = body

    def __repr__(self) -> str:
        return f'EachStatement({self.variable}, {self.iterable}, {self.body})'

class HaltStatement(Statement):
    """ Node representing a halt statement.

    Syntax:
        halt;

    Example:
        halt;
    """
    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return 'HaltStatement()'

class SkipStatement(Statement):
    """ Node representing a skip statement.

    Syntax:
        skip;

    Example:
        skip;
    """
    def __init__(self) -> None:
        pass
    def __repr__(self) -> str:
        return 'SkipStatement()'

class FunctionDeclaration(Statement):
    """ Node representing a function declaration.

    Args:
        name (str): The name of the function.
        function_type (FunctionType): The type of the function.
        body (BlockStatement): The block to be executed when the function is called.

    Syntax:
        func <name> -> <return type> = [<parameters>] >> <body>

    Example:
        func add -> int = [int x, int y] >> {
            return x + y;
        }
    """
    def __init__(self, name: str, function_type: FunctionType, body: BlockStatement) -> None:
        self.name = name
        self.function_type = function_type
        self.body = body

    def __repr__(self) -> str:
        return f'FunctionDeclaration({self.name}, {self.function_type}, {self.body})'

class ReturnStatement(Statement):
    """ Node representing a return statement.

    Args:
        expression (Optional[Expression]): The expression to be returned.

    Syntax:
        return <expression>;

    Example:
        return 5;
    """
    def __init__(self, expression: Optional[Expression]) -> None:
        self.expression = expression

    def __repr__(self) -> str:
        return f'ReturnStatement({self.expression})'

class EchoStatement(Statement):
    """ Node representing an echo statement.

    Args:
        expression (Expression): The expression to be echoed.

    Syntax:
        echo <expression>;

    Example:
        echo "Hello, World!";
    """
    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def __repr__(self) -> str:
        return f'EchoStatement({self.expression})'

# Expressions
class NumericLiteral(Expression):
    """ Node representing a numeric literal.

    Args:
        value (Union[int, float]): The value of the numeric literal.
    """
    def __init__(self, value: Union[int, float]) -> None:
        self.value = value
    def __repr__(self) -> str:
        return f'NumericLiteral({self.value})'

class StringLiteral(Expression):
    """ Node representing a string literal.

    Args:
        value (str): The value of the string literal.
    """
    def __init__(self, value: str) -> None:
        self.value = value
    def __repr__(self) -> str:
        return f'StringLiteral({self.value})'

class BooleanLiteral(Expression):
    """ Node representing a boolean literal.

    Args:
        value (bool): The value of the boolean literal.
    """
    def __init__(self, value: bool) -> None:
        self.value = value
    def __repr__(self) -> str:
        return f'BooleanLiteral({self.value})'

class NullLiteral(Expression):
    """ Node representing a null literal. """
    def __init__(self) -> None:
        self.value = None
    def __repr__(self) -> str:
        return f'NullLiteral()'

class ArrayLiteral(Expression):
    """ Node representing an array literal.

    Args:
        elements (List[Expression]): The elements of the array.
    """
    def __init__(self, elements: List[Expression]) -> None:
        self.elements = elements
    def __repr__(self) -> str:
        return f'ArrayLiteral({self.elements})'

class Identifier(Expression):
    """ Node representing an identifier.

    Args:
        name (str): The name of the identifier.
    """
    def __init__(self, name: str) -> None:
        self.name = name
    def __repr__(self) -> str:
        return f'Identifier({self.name})'

class UnaryExpression(Expression):
    """ Node representing a unary expression.

    Args:
        operator (TokenType): The operator of the unary expression.
        operand (Expression): The operand of the unary expression.
        position (Literal['PRE', 'POST']): The position of the operator.
    """
    def __init__(self, operator: TokenType, operand: Expression, position: Literal['PRE', 'POST']) -> None:
        self.operator = operator
        self.operand = operand
        self.position = position
    def __repr__(self) -> str:
        return f'UnaryExpression({self.operator}, {self.operand}, {self.position})'

class BinaryExpression(Expression):
    """ Node representing a binary expression.

    Args:
        left (Expression): The left operand of the binary expression.
        operator (TokenType): The operator of the binary expression.
        right (Expression): The right operand of the binary expression.
    """
    def __init__(self, left: Node, operator: TokenType, right: Node) -> None:
        self.left = left
        self.operator = operator
        self.right = right
    def __repr__(self) -> str:
        return f'BinaryExpression({self.left}, {self.operator}, {self.right})'

class AssignmentExpression(Expression):
    """ Node representing an assignment expression.

    Args:
        left (Node): The left operand of the assignment expression.
        right (Node): The right operand of the assignment expression.
    """
    def __init__(self, left: Node, right: Node) -> None:
        self.left = left
        self.right = right
    def __repr__(self) -> str:
        return f'AssignmentExpression({self.left}, {self.right})'

class IndexExpression(Expression):
    """ Node representing an index expression.

    Args:
        array (Expression): The array to be indexed.
        index (Expression): The index of the array.
    """
    def __init__(self, array: Expression, index: Expression) -> None:
        self.array = array
        self.index = index
    def __repr__(self) -> str:
        return f'IndexExpression({self.array}, {self.index})'

class CallExpression(Expression):
    """ Node representing a call expression.

    Args:
        callee (Identifier): The function to be called.
        args (List[Expression]): The arguments to be passed to the function.
    """
    def __init__(self, callee: Identifier, args: List[Expression]) -> None:
        self.callee = callee
        self.args = args
    def __repr__(self) -> str:
        return f'FunctionCall({self.callee}, {self.args})'
