from frontend.lexer.lexer import Lexer
from frontend.lexer.tokens import TokenType
from frontend.parser.parser import Parser
from frontend.semantic.types import ArrayType, PrimitiveType, SetType, MapType
from frontend.syntax.ast import *


def parse_code(code: str) -> Program:
    lexer = Lexer(code)
    tokens = list(lexer.tokenize())
    parser = Parser(tokens)
    return parser.parse()


def check(code: str, expected: Program):
    program = parse_code(code)
    assert repr(program) == repr(expected)


def test_variable_declaration():
    code = "int x = 5;"
    expected = Program(
        [VariableDeclaration("x", PrimitiveType(TokenType.INT), NumericLiteral(5))]
    )
    check(code, expected)


def test_expression_statement():
    code = "x + 10;"
    expected = Program(
        [
            ExpressionStatement(
                BinaryExpression(Identifier("x"), TokenType.PLUS, NumericLiteral(10))
            )
        ]
    )
    check(code, expected)


def test_block_statement():
    code = "{ float y = 1.5; y - 1; }"
    expected = Program(
        [
            BlockStatement(
                [
                    VariableDeclaration(
                        "y", PrimitiveType(TokenType.FLOAT), NumericLiteral(1.5)
                    ),
                    ExpressionStatement(
                        BinaryExpression(
                            Identifier("y"), TokenType.MINUS, NumericLiteral(1)
                        )
                    ),
                ]
            )
        ]
    )
    check(code, expected)


def test_echo_statement():
    code = "echo 'hello world';"
    expected = Program([EchoStatement(StringLiteral("hello world"))])
    check(code, expected)


def test_if_statement():
    code = """
        if (x > 5) {
            return x;
        } else {
            return 5;
        }
    """
    expected = Program(
        [
            IfStatement(
                BinaryExpression(Identifier("x"), TokenType.GT, NumericLiteral(5)),
                BlockStatement([ReturnStatement(Identifier("x"))]),
                BlockStatement([ReturnStatement(NumericLiteral(5))]),
            )
        ]
    )
    check(code, expected)


def test_nested_if_else():
    code = """
        bool is_true = true;
        if (x > 5) {
            if (is_true) {
                return y;
            } else {
                return x;
            }
        } else {
            return 5;
        }
    """
    expected = Program(
        [
            VariableDeclaration(
                "is_true", PrimitiveType(TokenType.BOOL), BooleanLiteral(True)
            ),
            IfStatement(
                BinaryExpression(Identifier("x"), TokenType.GT, NumericLiteral(5)),
                BlockStatement(
                    [
                        IfStatement(
                            Identifier("is_true"),
                            BlockStatement([ReturnStatement(Identifier("y"))]),
                            BlockStatement([ReturnStatement(Identifier("x"))]),
                        )
                    ]
                ),
                BlockStatement([ReturnStatement(NumericLiteral(5))]),
            ),
        ]
    )
    check(code, expected)


def test_unary_expressions():
    code = """
        x++;
        --y;
        !z;
    """
    expected = Program(
        [
            ExpressionStatement(
                UnaryExpression(TokenType.INCREMENT, Identifier("x"), "POST")
            ),
            ExpressionStatement(
                UnaryExpression(TokenType.DECREMENT, Identifier("y"), "PRE")
            ),
            ExpressionStatement(
                UnaryExpression(TokenType.LOGICAL_NOT, Identifier("z"), "PRE")
            ),
        ]
    )
    check(code, expected)


def test_complex_unary_expressions():
    code = """
        int x = a[1]++;
        int y = --b();
        bool z = !c();
    """

    excepted = Program(
        [
            VariableDeclaration(
                "x",
                PrimitiveType(TokenType.INT),
                UnaryExpression(
                    TokenType.INCREMENT,
                    IndexExpression(Identifier("a"), NumericLiteral(1)),
                    "POST",
                ),
            ),
            VariableDeclaration(
                "y",
                PrimitiveType(TokenType.INT),
                UnaryExpression(
                    TokenType.DECREMENT,
                    FunctionCallExpression(Identifier("b"), []),
                    "PRE",
                ),
            ),
            VariableDeclaration(
                "z",
                PrimitiveType(TokenType.BOOL),
                UnaryExpression(
                    TokenType.LOGICAL_NOT,
                    FunctionCallExpression(Identifier("c"), []),
                    "PRE",
                ),
            ),
        ]
    )
    check(code, excepted)


def test_logical_unary_expression():
    code = """ !x; """
    expected = Program(
        [
            ExpressionStatement(
                UnaryExpression(TokenType.LOGICAL_NOT, Identifier("x"), "PRE")
            )
        ]
    )
    check(code, expected)


def test_array_literal():
    code = "int[] arr = [1, 2, 3];"
    expected = Program(
        [
            VariableDeclaration(
                "arr",
                ArrayType(PrimitiveType(TokenType.INT)),
                ArrayLiteral([NumericLiteral(1), NumericLiteral(2), NumericLiteral(3)]),
            )
        ]
    )
    check(code, expected)


def test_array_indexing():
    code = "int[] x = arr[0];"
    expected = Program(
        [
            VariableDeclaration(
                "x",
                ArrayType(PrimitiveType(TokenType.INT)),
                IndexExpression(Identifier("arr"), NumericLiteral(0)),
            )
        ]
    )
    check(code, expected)


def test_combined_array_example():
    code = """
        int[] arr = [1, 2, 3];
        int x = arr[1];
        arr[2] = 5;
    """
    expected = Program(
        [
            VariableDeclaration(
                "arr",
                ArrayType(PrimitiveType(TokenType.INT)),
                ArrayLiteral([NumericLiteral(1), NumericLiteral(2), NumericLiteral(3)]),
            ),
            VariableDeclaration(
                "x",
                PrimitiveType(TokenType.INT),
                IndexExpression(Identifier("arr"), NumericLiteral(1)),
            ),
            ExpressionStatement(
                AssignmentExpression(
                    IndexExpression(Identifier("arr"), NumericLiteral(2)),
                    NumericLiteral(5),
                )
            ),
        ]
    )
    check(code, expected)


def test_set_literal():
    code = """
        int{} x = {1, 2, 3};
    """
    expected = Program(
        [
            VariableDeclaration(
                "x",
                SetType(PrimitiveType(TokenType.INT)),
                SetLiteral([NumericLiteral(1), NumericLiteral(2), NumericLiteral(3)]),
            )
        ]
    )
    check(code, expected)


def test_map_literal():
    code = """
        int{str} x = {"a": 1, "b": 2};
    """
    expected = Program(
        [
            VariableDeclaration(
                "x",
                MapType(PrimitiveType(TokenType.STR), PrimitiveType(TokenType.INT)),
                MapLiteral(
                    [
                        (StringLiteral("a"), NumericLiteral(1)),
                        (StringLiteral("b"), NumericLiteral(2)),
                    ]
                ),
            )
        ]
    )
    check(code, expected)


def test_set_method_call():
    code = """
        int{} x = {1, 2, 3};
        x.add(4).remove(2);
    """

    expected = Program(
        [
            VariableDeclaration(
                "x",
                SetType(PrimitiveType(TokenType.INT)),
                SetLiteral([NumericLiteral(1), NumericLiteral(2), NumericLiteral(3)]),
            ),
            ExpressionStatement(
                MethodCallExpression(
                    MethodCallExpression(
                        Identifier("x"), Identifier("add"), [NumericLiteral(4)]
                    ),
                    Identifier("remove"),
                    [NumericLiteral(2)],
                )
            ),
        ]
    )
    check(code, expected)


def test_map_method_call():
    code = """
        int{str} y = {"a": 1, "b": 2};
        int b = y.set("c", 3).remove("a").get("b");
        y.clear();
    """
    expected = Program(
        [
            VariableDeclaration(
                "y",
                MapType(PrimitiveType(TokenType.STR), PrimitiveType(TokenType.INT)),
                MapLiteral(
                    [
                        (StringLiteral("a"), NumericLiteral(1)),
                        (StringLiteral("b"), NumericLiteral(2)),
                    ]
                ),
            ),
            VariableDeclaration(
                "b",
                PrimitiveType(TokenType.INT),
                MethodCallExpression(
                    MethodCallExpression(
                        MethodCallExpression(
                            Identifier("y"),
                            Identifier("set"),
                            [StringLiteral("c"), NumericLiteral(3)],
                        ),
                        Identifier("remove"),
                        [StringLiteral("a")],
                    ),
                    Identifier("get"),
                    [StringLiteral("b")],
                ),
            ),
            ExpressionStatement(
                MethodCallExpression(Identifier("y"), Identifier("clear"), [])
            ),
        ]
    )
    check(code, expected)


def test_complex_collection_type():
    code = """
        // Array of array of maps with int set keys and string values
        str{int{}}[][] x = [[{{1, 2, 3}: 'hello', {4, 5, 6}: 'world'}]];
    """
    expected = Program(
        [
            VariableDeclaration(
                "x",
                ArrayType(
                    ArrayType(
                        MapType(
                            SetType(PrimitiveType(TokenType.INT)),
                            PrimitiveType(TokenType.STR),
                        ),
                    )
                ),
                ArrayLiteral(
                    [
                        ArrayLiteral(
                            [
                                MapLiteral(
                                    [
                                        (
                                            SetLiteral(
                                                [
                                                    NumericLiteral(1),
                                                    NumericLiteral(2),
                                                    NumericLiteral(3),
                                                ]
                                            ),
                                            StringLiteral("hello"),
                                        ),
                                        (
                                            SetLiteral(
                                                [
                                                    NumericLiteral(4),
                                                    NumericLiteral(5),
                                                    NumericLiteral(6),
                                                ]
                                            ),
                                            StringLiteral("world"),
                                        ),
                                    ]
                                )
                            ]
                        )
                    ]
                ),
            )
        ]
    )
    check(code, expected)


def test_while_statement():
    code = """
        while (x < 10) {
            x++;
        }
    """
    expected = Program(
        [
            WhileStatement(
                BinaryExpression(Identifier("x"), TokenType.LT, NumericLiteral(10)),
                BlockStatement(
                    [
                        ExpressionStatement(
                            UnaryExpression(
                                TokenType.INCREMENT, Identifier("x"), "POST"
                            )
                        )
                    ]
                ),
            )
        ]
    )
    check(code, expected)


def test_each_statement():
    code = """
        each (x in [1, 2, 3]) {
            return x;
        }
    """

    expected = Program(
        [
            EachStatement(
                "x",
                ArrayLiteral([NumericLiteral(1), NumericLiteral(2), NumericLiteral(3)]),
                BlockStatement([ReturnStatement(Identifier("x"))]),
            )
        ]
    )
    check(code, expected)


def test_range_statement():
    code = """
        range (x in 0 to 10) {
            return x;
        }
    """
    expected = Program(
        [
            RangeStatement(
                "x",
                NumericLiteral(0),
                NumericLiteral(10),
                NumericLiteral(1),
                BlockStatement([ReturnStatement(Identifier("x"))]),
            )
        ]
    )
    check(code, expected)


def test_halt_statement():
    code = """
        range (x in 0 to 10) {
            if (x == 5) {
                halt;
            }
        }
    """
    expected = Program(
        [
            RangeStatement(
                "x",
                NumericLiteral(0),
                NumericLiteral(10),
                NumericLiteral(1),
                BlockStatement(
                    [
                        IfStatement(
                            BinaryExpression(
                                Identifier("x"), TokenType.EQUAL, NumericLiteral(5)
                            ),
                            BlockStatement([HaltStatement()]),
                            None,
                        )
                    ]
                ),
            )
        ]
    )
    check(code, expected)


def test_skip_statement():
    code = """
        each (x in [1, 2, 3, 4]) {
            if (isEven(x)) {
                skip;
            }
        }
    """

    expected = Program(
        [
            EachStatement(
                "x",
                ArrayLiteral(
                    [
                        NumericLiteral(1),
                        NumericLiteral(2),
                        NumericLiteral(3),
                        NumericLiteral(4),
                    ]
                ),
                BlockStatement(
                    [
                        IfStatement(
                            FunctionCallExpression(
                                Identifier("isEven"), [Identifier("x")]
                            ),
                            BlockStatement([SkipStatement()]),
                            None,
                        )
                    ]
                ),
            )
        ]
    )
    check(code, expected)


def test_function_declaration():
    code = """
        func add -> int = [int a, int b] >> {
            return a + b;
        }
    """
    expected = Program(
        [
            FunctionDeclaration(
                "add",
                FunctionType(
                    PrimitiveType(TokenType.INT),
                    [
                        ("a", PrimitiveType(TokenType.INT)),
                        ("b", PrimitiveType(TokenType.INT)),
                    ],
                ),
                BlockStatement(
                    [
                        ReturnStatement(
                            BinaryExpression(
                                Identifier("a"), TokenType.PLUS, Identifier("b")
                            )
                        )
                    ]
                ),
            )
        ]
    )
    check(code, expected)


def test_combined_function_example():
    code = """
        int z = 15;
        func multiply -> int = [int x, int y] >> {
            return x * y;
        }
        if (z > 10) {
            z = multiply(z, 2);
        }
        while (z > 0) {
            z = z - 1;
        }
    """
    expected = Program(
        [
            VariableDeclaration("z", PrimitiveType(TokenType.INT), NumericLiteral(15)),
            FunctionDeclaration(
                "multiply",
                FunctionType(
                    PrimitiveType(TokenType.INT),
                    [
                        ("x", PrimitiveType(TokenType.INT)),
                        ("y", PrimitiveType(TokenType.INT)),
                    ],
                ),
                BlockStatement(
                    [
                        ReturnStatement(
                            BinaryExpression(
                                Identifier("x"), TokenType.MULTIPLY, Identifier("y")
                            )
                        )
                    ]
                ),
            ),
            IfStatement(
                BinaryExpression(Identifier("z"), TokenType.GT, NumericLiteral(10)),
                BlockStatement(
                    [
                        ExpressionStatement(
                            AssignmentExpression(
                                Identifier("z"),
                                FunctionCallExpression(
                                    Identifier("multiply"),
                                    [Identifier("z"), NumericLiteral(2)],
                                ),
                            )
                        )
                    ]
                ),
                None,
            ),
            WhileStatement(
                BinaryExpression(Identifier("z"), TokenType.GT, NumericLiteral(0)),
                BlockStatement(
                    [
                        ExpressionStatement(
                            AssignmentExpression(
                                Identifier("z"),
                                BinaryExpression(
                                    Identifier("z"), TokenType.MINUS, NumericLiteral(1)
                                ),
                            )
                        )
                    ]
                ),
            ),
        ]
    )
    check(code, expected)


def test_arg_function_type():
    code = """
        func add -> int = [int a, int b] >> {
            return a + b;
        }

        func reduce -> int = [int[] arr, func<int, [int a, int b]> fn] >> {
            int result = 0;
            each (x in arr) {
                result = fn(result, x);
            }
            return result;
        }
    """

    excepted = Program(
        [
            FunctionDeclaration(
                "add",
                FunctionType(
                    PrimitiveType(TokenType.INT),
                    [
                        ("a", PrimitiveType(TokenType.INT)),
                        ("b", PrimitiveType(TokenType.INT)),
                    ],
                ),
                BlockStatement(
                    [
                        ReturnStatement(
                            BinaryExpression(
                                Identifier("a"), TokenType.PLUS, Identifier("b")
                            )
                        )
                    ]
                ),
            ),
            FunctionDeclaration(
                "reduce",
                FunctionType(
                    PrimitiveType(TokenType.INT),
                    [
                        ("arr", ArrayType(PrimitiveType(TokenType.INT))),
                        (
                            "fn",
                            FunctionType(
                                PrimitiveType(TokenType.INT),
                                [
                                    ("a", PrimitiveType(TokenType.INT)),
                                    ("b", PrimitiveType(TokenType.INT)),
                                ],
                            ),
                        ),
                    ],
                ),
                BlockStatement(
                    [
                        VariableDeclaration(
                            "result", PrimitiveType(TokenType.INT), NumericLiteral(0)
                        ),
                        EachStatement(
                            "x",
                            Identifier("arr"),
                            BlockStatement(
                                [
                                    ExpressionStatement(
                                        AssignmentExpression(
                                            Identifier("result"),
                                            FunctionCallExpression(
                                                Identifier("fn"),
                                                [Identifier("result"), Identifier("x")],
                                            ),
                                        )
                                    )
                                ]
                            ),
                        ),
                        ReturnStatement(Identifier("result")),
                    ]
                ),
            ),
        ]
    )

    check(code, excepted)


def test_pipe_expression_single():
    code = """
        [[1, 2, 3]] >> map(triple);
    """
    expected = Program(
        [
            ExpressionStatement(
                FunctionCallExpression(
                    Identifier("map"),
                    [
                        ArrayLiteral(
                            [NumericLiteral(1), NumericLiteral(2), NumericLiteral(3)]
                        ),
                        Identifier("triple"),
                    ],
                )
            )
        ]
    )
    check(code, expected)


def test_pipe_expression_multiple():
    code = """
        [[1, 2, 3]] >> map(triple) >> filter(isEven) >> reduce(add);
    """
    expected = Program(
        [
            ExpressionStatement(
                FunctionCallExpression(
                    Identifier("reduce"),
                    [
                        FunctionCallExpression(
                            Identifier("filter"),
                            [
                                FunctionCallExpression(
                                    Identifier("map"),
                                    [
                                        ArrayLiteral(
                                            [
                                                NumericLiteral(1),
                                                NumericLiteral(2),
                                                NumericLiteral(3),
                                            ]
                                        ),
                                        Identifier("triple"),
                                    ],
                                ),
                                Identifier("isEven"),
                            ],
                        ),
                        Identifier("add"),
                    ],
                )
            )
        ]
    )
    check(code, expected)


def test_complex_pipe_expression():
    code = """
        int[] x = [[1, 2], [3, 4]]
            >> reduce(add)
            >> map(triple)
            >> sum;
    """
    expected = Program(
        [
            VariableDeclaration(
                "x",
                ArrayType(PrimitiveType(TokenType.INT)),
                FunctionCallExpression(
                    Identifier("sum"),
                    [
                        FunctionCallExpression(
                            Identifier("map"),
                            [
                                FunctionCallExpression(
                                    Identifier("reduce"),
                                    [
                                        ArrayLiteral(
                                            [NumericLiteral(1), NumericLiteral(2)]
                                        ),
                                        ArrayLiteral(
                                            [NumericLiteral(3), NumericLiteral(4)]
                                        ),
                                        Identifier("add"),
                                    ],
                                ),
                                Identifier("triple"),
                            ],
                        )
                    ],
                ),
            )
        ]
    )
    check(code, expected)


def test_comments():
    code = """
        // This is a single line comment
        int x = 5; // This is another comment
        // echo 'This code should be ignored';
        echo 'This should be included';
        /* This is a
        multi-line comment */
    """
    expected = Program(
        [
            VariableDeclaration("x", PrimitiveType(TokenType.INT), NumericLiteral(5)),
            EchoStatement(StringLiteral("This should be included")),
        ]
    )
    check(code, expected)


def test_template_declaration():
    code = """
        template Person = {
            str name;
            int age;
            
            func greet -> void = [str greeting] >> {
                echo greeting;
            }
        };
    """
    expected = Program(
        [
            TemplateDeclaration(
                "Person",
                {
                    "name": PrimitiveType(TokenType.STR),
                    "age": PrimitiveType(TokenType.INT),
                },
                {
                    "greet": FunctionDeclaration(
                        "greet",
                        FunctionType(
                            PrimitiveType(TokenType.VOID),
                            [("greeting", PrimitiveType(TokenType.STR))],
                        ),
                        BlockStatement([EchoStatement(Identifier("greeting"))]),
                    ),
                },
            )
        ]
    )
    check(code, expected)


def test_entity_declaration():
    code = """
        entity character = Person{
            name: 'Alice',
            age: 25
        };
    """
    expected = Program(
        [
            VariableDeclaration(
                "character",
                CustomTypeIdentifier("Person"),
                EntityLiteral(
                    CustomTypeIdentifier("Person"),
                    {"name": StringLiteral("Alice"), "age": NumericLiteral(25)},
                ),
            )
        ]
    )
    check(code, expected)


def test_member_access_expression():
    code = """
        int x = foo.bar.baz.qux;
    """
    excepted = Program(
        [
            VariableDeclaration(
                "x",
                PrimitiveType(TokenType.INT),
                MemberAccessExpression(
                    MemberAccessExpression(
                        MemberAccessExpression(Identifier("foo"), Identifier("bar")),
                        Identifier("baz"),
                    ),
                    Identifier("qux"),
                ),
            )
        ]
    )
    check(code, excepted)
    
def test_property_assignment_expression():
    code = """
        foo.bar.baz.qux = 5;
    """
    excepted = Program(
        [
            ExpressionStatement(
                AssignmentExpression(
                    MemberAccessExpression(
                        MemberAccessExpression(
                            MemberAccessExpression(Identifier("foo"), Identifier("bar")),
                            Identifier("baz"),
                        ),
                        Identifier("qux"),
                    ),
                    NumericLiteral(5),
                )
            )
        ]
    )
    check(code, excepted)