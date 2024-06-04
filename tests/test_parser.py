from lexer.lexer import Lexer
from lexer.tokens import TokenType
from parser.parser import Parser
from syntax.ast import *

def parse_code(code: str) -> Program:
    lexer = Lexer(code)
    tokens = list(lexer.tokenize())
    parser = Parser(tokens)
    return parser.parse()

def check(code: str, expected: Program):
    program = parse_code(code)
    assert repr(program) == repr(expected)

def test_variable_declaration():
    code = "let x = 5;"
    expected = Program([
        VariableDeclaration("x", NumericLiteral(5))
    ])
    check(code, expected)

def test_expression_statement():
    code = "x + 10;"
    expected = Program([
        ExpressionStatement(BinaryExpression(Identifier("x"), TokenType.PLUS, NumericLiteral(10)))
    ])
    check(code, expected)

def test_block_statement():
    code = "{ let y = 20; y - 5; }"
    expected = Program([
        BlockStatement([
            VariableDeclaration("y", NumericLiteral(20)),
            ExpressionStatement(BinaryExpression(Identifier("y"), TokenType.MINUS, NumericLiteral(5)))
        ])
    ])
    check(code, expected)

def test_echo_statement():
    code = "echo 'hello world';"
    expected = Program([
        EchoStatement(StringLiteral("hello world"))
    ])
    check(code, expected)

def test_if_statement():
    code = """
        if (x > 5) {
            return x;
        } else {
            return 5;
        }
    """
    expected = Program([
        IfStatement(
            BinaryExpression(Identifier("x"), TokenType.GT, NumericLiteral(5)),
            BlockStatement([ReturnStatement(Identifier("x"))]),
            BlockStatement([ReturnStatement(NumericLiteral(5))])
        )
    ])
    check(code, expected)

def test_nested_if_else():
    code = """
        if (x > 5) {
            if (y < 10) {
                return y;
            } else {
                return x;
            }
        } else {
            return 5;
        }
    """
    expected = Program([
        IfStatement(
            BinaryExpression(Identifier("x"), TokenType.GT, NumericLiteral(5)),
            BlockStatement([
                IfStatement(
                    BinaryExpression(Identifier("y"), TokenType.LT, NumericLiteral(10)),
                    BlockStatement([ReturnStatement(Identifier("y"))]),
                    BlockStatement([ReturnStatement(Identifier("x"))])
                )
            ]),
            BlockStatement([ReturnStatement(NumericLiteral(5))])
        )
    ])
    check(code, expected)

def test_while_statement():
    code = """
        while (x < 10) {
            x++;
        }
    """
    expected = Program([
        WhileStatement(
            BinaryExpression(Identifier("x"), TokenType.LT, NumericLiteral(10)),
            BlockStatement([
                ExpressionStatement(
                    UnaryExpression(TokenType.INCREMENT, Identifier("x"), 'POST')
                )
            ])
        )
    ])
    check(code, expected)

def test_array_literal():
    code = "let arr = [1, 2, 3];"
    expected = Program([
        VariableDeclaration("arr", ArrayLiteral([
            NumericLiteral(1),
            NumericLiteral(2),
            NumericLiteral(3)
        ]))
    ])
    check(code, expected)

def test_array_indexing():
    code = "let x = arr[0];"
    expected = Program([
        VariableDeclaration("x", IndexExpression(
            Identifier("arr"),
            NumericLiteral(0)
        ))
    ])
    check(code, expected)

def test_combined_array_example():
    code = """
        let arr = [1, 2, 3];
        let x = arr[1];
        arr[2] = 5;
    """
    expected = Program([
        VariableDeclaration("arr", ArrayLiteral([
            NumericLiteral(1),
            NumericLiteral(2),
            NumericLiteral(3)
        ])),
        VariableDeclaration("x", IndexExpression(
            Identifier("arr"),
            NumericLiteral(1)
        )),
        ExpressionStatement(AssignmentExpression(
            IndexExpression(
                Identifier("arr"),
                NumericLiteral(2)
            ),
            NumericLiteral(5)
        ))
    ])
    check(code, expected)

def test_each_statement():
    code = """
        each x in [1, 2, 3] {
            return x;
        }
    """

    expected = Program([
        EachStatement(
            "x",
            ArrayLiteral([NumericLiteral(1), NumericLiteral(2), NumericLiteral(3)]),
            BlockStatement([ReturnStatement(Identifier("x"))])
        )
    ])
    check(code, expected)

def test_range_statement():
    code = """
        range x in 0 to 10 {
            return x;
        }
    """
    expected = Program([
        RangeStatement(
            "x",
            NumericLiteral(0),
            NumericLiteral(10),
            NumericLiteral(1),
            BlockStatement([ReturnStatement(Identifier("x"))])
        )
    ])
    check(code, expected)

def test_function_declaration():
    code = """
        func add = [a, b] >> {
            return a + b;
        }
    """
    expected = Program([
        FunctionDeclaration("add", ["a", "b"], BlockStatement([ReturnStatement(BinaryExpression(Identifier("a"), TokenType.PLUS, Identifier("b")))]))
    ])
    check(code, expected)

def test_combined_function_example():
    code = """
        let z = 15;
        func multiply = [x, y] >> {
            return x * y;
        }
        if (z > 10) {
            z = multiply(z, 2);
        }
        while (z > 0) {
            z = z - 1;
        }
    """
    expected = Program([
        VariableDeclaration("z", NumericLiteral(15)),
        FunctionDeclaration("multiply", ["x", "y"], BlockStatement([ReturnStatement(BinaryExpression(Identifier("x"), TokenType.MULTIPLY, Identifier("y")))])),
        IfStatement(
            BinaryExpression(Identifier("z"), TokenType.GT, NumericLiteral(10)),
            BlockStatement([ExpressionStatement(AssignmentExpression(Identifier("z"),  CallExpression(Identifier("multiply"), [Identifier("z"), NumericLiteral(2)])))]),
            None
        ),
        WhileStatement(
            BinaryExpression(Identifier("z"), TokenType.GT, NumericLiteral(0)),
            BlockStatement([ExpressionStatement(AssignmentExpression(Identifier("z"), BinaryExpression(Identifier("z"), TokenType.MINUS, NumericLiteral(1))))])
        )
    ])
    check(code, expected)

def test_pipe_expression_single():
    code = """
        [[1, 2, 3]] >> map(triple);
    """
    expected = Program([
        ExpressionStatement(
            PipeExpression(
                [ArrayLiteral([NumericLiteral(1), NumericLiteral(2), NumericLiteral(3)])],
                [CallExpression(Identifier("map"), [Identifier("triple")])]
            )
        )
    ])
    check(code, expected)

def test_pipe_expression_multiple():
    code = """
        [[1, 2, 3]] >> map(triple) >> filter(isEven) >> reduce(add);
    """
    expected = Program([
        ExpressionStatement(
            PipeExpression(
                [ArrayLiteral([NumericLiteral(1), NumericLiteral(2), NumericLiteral(3)])],
                [
                    CallExpression(Identifier("map"), [Identifier("triple")]),
                    CallExpression(Identifier("filter"), [Identifier("isEven")]),
                    CallExpression(Identifier("reduce"), [Identifier("add")])
                ]
            )
        )
    ])
    check(code, expected)

def test_complex_pipe_expression():
    code = """
        let x = [[1, 2], [3, 4]]
            >> reduce(add)
            >> map(triple)
            >> sum;
    """
    expected = Program([
        VariableDeclaration("x", PipeExpression(
            [
                ArrayLiteral([NumericLiteral(1), NumericLiteral(2)]),
                ArrayLiteral([NumericLiteral(3), NumericLiteral(4)])
            ],
            [
                CallExpression(Identifier("reduce"), [Identifier("add")]),
                CallExpression(Identifier("map"), [Identifier("triple")]),
                Identifier("sum")
            ]
        ))
    ])
    check(code, expected)

def test_comments():
    code = """
        // This is a single line comment
        let x = 5; // This is another comment
        // echo 'This code should be ignored';
        echo 'This should be included';
        /* This is a
        multi-line comment */
    """
    expected = Program([
        VariableDeclaration("x", NumericLiteral(5)),
        EchoStatement(StringLiteral("This should be included"))
    ])
    check(code, expected)
