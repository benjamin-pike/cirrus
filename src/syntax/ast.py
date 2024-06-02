from typing import *
from lexer.tokens import TokenType

class Node: pass
class Statement(Node): pass
class Expression(Node): pass

# Program
class Program(Statement):
    def __init__(self, body: List[Statement]) -> None:
        self.body: List[Statement] = body
    def __repr__(self) -> str:
        return f'Program({self.body})'

# Statements
"""
1. Variable Declaration Statement
   Syntax: let <variable_name> = <initializer>;

    let x = 5;
"""
class VariableDeclaration(Statement):
    def __init__(self, name: str, initializer: Node) -> None:
        self.type = "VariableDeclaration"
        self.name = name
        self.initializer = initializer
    def __repr__(self) -> str:
        return f'VariableDeclaration({self.name}, {self.initializer})'

"""
2.  Expression Statement
    Syntax: <expression>;
    
    5 + 5;
"""
class ExpressionStatement(Statement):
    def __init__(self, expression: Node) -> None:
        self.type = "ExpressionStatement"
        self.expression = expression
    def __repr__(self) -> str:
        return f'ExpressionStatement({self.expression})'
    
"""
3.  Block Statement
    Syntax: { <statements> }
    
    {
        let x = 5;
        let y = 10;
    }
"""
class BlockStatement(Statement):
    def __init__(self, statements: List[Statement]) -> None:
        self.type = "BlockStatement"
        self.statements = statements

    def __repr__(self) -> str:
        return f'BlockStatement({self.statements})'

"""
4. If Statement
    Syntax: if <condition> <then_branch> else <else_branch>
    
    if x > 5 {
        return x;
    } else {
        return 5;
    }
"""
class IfStatement(Statement):
    def __init__(self, condition: Expression, then_block: BlockStatement, else_block: Optional[BlockStatement]) -> None:
        self.type = "IfStatement"
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def __repr__(self) -> str:
        return f'IfStatement({self.condition}, {self.then_block}, {self.else_block})'

"""
5. While Statement
    Syntax: while <condition> <body>
    
    while x < 5 {
        x = x + 1;
    }
"""
class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: BlockStatement) -> None:
        self.type = "WhileStatement"
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f'WhileStatement({self.condition}, {self.body})'

"""
6.  Range Statement
    Syntax: range <identifier> in <start> to <end> by <increment> <body>

    range i in 0 to 10 by 1 {
        echo i;
    }
"""
class RangeStatement(Statement):
    def __init__(self, identifier: str, start: Expression, end: Expression, increment: Expression, body: BlockStatement) -> None:
        self.type = "RangeStatement"
        self.identifier = identifier
        self.start = start
        self.end = end
        self.increment = increment
        self.body = body

    def __repr__(self) -> str:
        return f'RangeStatement({self.identifier}, {self.start}, {self.end}, {self.increment}, {self.body})'
        

"""
7.  Each Statement
    Syntax: each <variable> in <iterable> <body>

    each item in items {
        echo item;
    }
"""
class EachStatement(Statement):
    def __init__(self, variable: str, iterable: Expression, body: BlockStatement) -> None:
        self.type = "EachStatement"
        self.variable = variable
        self.iterable = iterable
        self.body = body

    def __repr__(self) -> str:
        return f'EachStatement({self.variable}, {self.iterable}, {self.body})'

"""
8.  Return Statement
    Syntax: return <expression>;

    return 5;
"""
class ReturnStatement(Statement):
    def __init__(self, expression: Optional[Expression]) -> None:
        self.type = "ReturnStatement"
        self.expression = expression

    def __repr__(self) -> str:
        return f'ReturnStatement({self.expression})'

"""
9.  Function Declaration
    Syntax: func <name> = [<parameters>] >> <body>
    
    func add = [x, y] >> {
        return x + y;
    }
"""
class FunctionDeclaration(Statement):
    def __init__(self, name: str, parameters: List[str], body: BlockStatement) -> None:
        self.type = "FunctionDeclaration"
        self.name = name
        self.parameters = parameters
        self.body = body

    def __repr__(self) -> str:
        return f'FunctionDeclaration({self.name}, {self.parameters}, {self.body})'
    
"""
10. Echo Statement
    Syntax: echo <expression>;
    
    echo "Hello, World!";
"""
class EchoStatement(Statement):
    def __init__(self, expression: Expression) -> None:
        self.type = "EchoStatement"
        self.expression = expression

    def __repr__(self) -> str:
        return f'EchoStatement({self.expression})'

# Expressions
class NumericLiteral(Expression):
    def __init__(self, value: Union[int, float]) -> None:
        self.value = value
    def __repr__(self) -> str:
        return f'NumericLiteral({self.value})'
    
class StringLiteral(Expression):
    def __init__(self, value: str) -> None:
        self.value = value
    def __repr__(self) -> str:
        return f'StringLiteral({self.value})'
    
class BooleanLiteral(Expression):
    def __init__(self, value: bool) -> None:
        self.value = value
    def __repr__(self) -> str:
        return f'BooleanLiteral({self.value})'
    
class NullLiteral(Expression):
    def __init__(self) -> None:
        self.value = None
    def __repr__(self) -> str:
        return f'NullLiteral()'
    
class ArrayLiteral(Expression):
    def __init__(self, elements: List[Expression]) -> None:
        self.elements = elements
    def __repr__(self) -> str:
        return f'ArrayLiteral({self.elements})'

class Identifier(Expression):
    def __init__(self, name: str) -> None:
        self.name = name
    def __repr__(self) -> str:
        return f'Identifier({self.name})'
    
class UnaryExpression(Expression):
    def __init__(self, operator: TokenType, operand: Expression, position: Literal['PRE', 'POST']) -> None:
        self.operator = operator
        self.operand = operand
        self.position = position
    def __repr__(self) -> str:
        return f'UnaryExpression({self.operator}, {self.operand}, {self.position})'

class BinaryExpression(Expression):
    def __init__(self, left: Node, operator: TokenType, right: Node) -> None:
        self.left = left
        self.operator = operator
        self.right = right
    def __repr__(self) -> str:
        return f'BinaryExpression({self.left}, {self.operator}, {self.right})'
    
class AssignmentExpression(Expression):
    def __init__(self, left: Node, right: Node) -> None:
        self.left = left
        self.right = right
    def __repr__(self) -> str:
        return f'AssignmentExpression({self.left}, {self.right})'

class IndexExpression(Expression):
    def __init__(self, array: Expression, index: Expression) -> None:
        self.array = array
        self.index = index
    def __repr__(self) -> str:
        return f'IndexExpression({self.array}, {self.index})'
    
class CallExpression(Expression):
    def __init__(self, callee: Node, arguments: List[Expression]) -> None:
        self.callee = callee
        self.arguments = arguments
    def __repr__(self) -> str:
        return f'FunctionCall({self.callee}, {self.arguments})'