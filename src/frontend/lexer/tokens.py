from enum import Enum, auto


class TokenType(Enum):
    """Enum class representing the tokens used the language."""

    # Keywords
    RETURN = auto()  # "return"
    IF = auto()  # "if"
    ELSE = auto()  # "else"
    WHILE = auto()  # "while"
    RANGE = auto()  # "range"
    EACH = auto()  # "each"
    FUNC = auto()  # "func"
    ECHO = auto()  # "echo"
    IN = auto()  # "in"
    TO = auto()  # "to"
    BY = auto()  # "by"
    HALT = auto()  # "halt"
    SKIP = auto()  # "skip"

    INT = auto()  # "int"
    FLOAT = auto()  # "float"
    BOOL = auto()  # "bool"
    STR = auto()  # "str"
    NULL = auto()  # "null"
    INFER = auto()  # "infer"
    VOID = auto()  # "void"
    TEMPLATE = auto()  # "template"
    ENTITY = auto()  # "entity"

    # Identifiers
    IDENTIFIER = auto()

    # Delimiters
    LPAREN = auto()  # "("
    RPAREN = auto()  # ")"
    LBRACE = auto()  # "{"
    RBRACE = auto()  # "}"
    LBRACKET = auto()  # "["
    RBRACKET = auto()  # "]"

    DOT = auto()  # "."
    COMMA = auto()  # ","
    SEMICOLON = auto()  # ";"
    COLON = auto()  # ":"
    ARROW = auto()  # ">>"
    RT_ARROW = auto()  # "->"

    # Literals
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()
    BOOLEAN_LITERAL = auto()
    NULL_LITERAL = auto()
    STRING_LITERAL = auto()

    # Operators
    # Arithmetic
    PLUS = auto()  # "+"
    MINUS = auto()  # "-"
    MULTIPLY = auto()  # "*"
    DIVIDE = auto()  # "/"

    # Assignment
    ASSIGN = auto()  # "="
    PLUS_ASSIGN = auto()  # "+="
    MINUS_ASSIGN = auto()  # "-="
    MULTIPLY_ASSIGN = auto()  # "*="
    DIVIDE_ASSIGN = auto()  # "/="

    # Logical
    LOGICAL_AND = auto()  # "&&"
    LOGICAL_OR = auto()  # "||"
    LOGICAL_NOT = auto()  # "!"

    # Comparitive
    EQUAL = auto()  # "=="
    NOT_EQUAL = auto()  # "!="
    LT = auto()  # "<"
    GT = auto()  # ">"
    LTE = auto()  # "<="
    GTE = auto()  # ">="

    # Unary
    INCREMENT = auto()  # "++"
    DECREMENT = auto()  # "--"

    # String delimiters
    DOUBLE_QUOTE = auto()  # '"'
    SINGLE_QUOTE = auto()  # '\''

    # Comments
    EOL_COMMENT = auto()  # "// ... \n"
    DELIMITED_COMMENT = auto()  # "/* ... */"

    # End of file
    EOF = auto()

    # Other
    GAP = auto()
    NEWLINE = auto()
    MISMATCH = auto()


spec = (
    (TokenType.RETURN, r"\breturn\b"),
    (TokenType.IF, r"\bif\b"),
    (TokenType.ELSE, r"\belse\b"),
    (TokenType.WHILE, r"\bwhile\b"),
    (TokenType.RANGE, r"\brange\b"),
    (TokenType.EACH, r"\beach\b"),
    (TokenType.FUNC, r"\bfunc\b"),
    (TokenType.ECHO, r"\becho\b"),
    (TokenType.IN, r"\bin\b"),
    (TokenType.TO, r"\bto\b"),
    (TokenType.BY, r"\bby\b"),
    (TokenType.HALT, r"\bhalt\b"),
    (TokenType.SKIP, r"\bskip\b"),
    (TokenType.INT, r"\bint\b"),
    (TokenType.FLOAT, r"\bfloat\b"),
    (TokenType.BOOL, r"\bbool\b"),
    (TokenType.STR, r"\bstr\b"),
    (TokenType.INFER, r"\binfer\b"),
    (TokenType.VOID, r"\bvoid\b"),
    (TokenType.TEMPLATE, r"\btemplate\b"),
    (TokenType.ENTITY, r"\bentity\b"),
    (TokenType.LPAREN, r"\("),
    (TokenType.RPAREN, r"\)"),
    (TokenType.LBRACE, r"\{"),
    (TokenType.RBRACE, r"\}"),
    (TokenType.LBRACKET, r"\["),
    (TokenType.RBRACKET, r"\]"),
    (TokenType.DOT, r"\."),
    (TokenType.COMMA, r","),
    (TokenType.SEMICOLON, r";"),
    (TokenType.COLON, r":"),
    (TokenType.ARROW, r">>"),
    (TokenType.RT_ARROW, r"->"),
    (TokenType.EOL_COMMENT, r"//.*\n"),
    (TokenType.DELIMITED_COMMENT, r"/\*[\s\S]*?(?:\*/|$)"),
    (TokenType.LOGICAL_AND, r"&&"),
    (TokenType.LOGICAL_OR, r"\|\|"),
    (TokenType.LOGICAL_NOT, r"!"),
    (TokenType.INCREMENT, r"\+\+"),
    (TokenType.DECREMENT, r"--"),
    (TokenType.EQUAL, r"=="),
    (TokenType.NOT_EQUAL, r"!="),
    (TokenType.LTE, r"<="),
    (TokenType.GTE, r">="),
    (TokenType.LT, r"<"),
    (TokenType.GT, r">"),
    (TokenType.ASSIGN, r"="),
    (TokenType.PLUS_ASSIGN, r"\+="),
    (TokenType.MINUS_ASSIGN, r"-="),
    (TokenType.MULTIPLY_ASSIGN, r"\*="),
    (TokenType.DIVIDE_ASSIGN, r"/="),
    (TokenType.PLUS, r"\+"),
    (TokenType.MINUS, r"-"),
    (TokenType.MULTIPLY, r"\*"),
    (TokenType.DIVIDE, r"/"),
    (TokenType.BOOLEAN_LITERAL, r"\btrue\b|\bfalse\b"),
    (TokenType.NULL_LITERAL, r"\bnull\b"),
    (TokenType.FLOAT_LITERAL, r"\d+\.\d+"),
    (TokenType.INT_LITERAL, r"\d+"),
    (TokenType.DOUBLE_QUOTE, r'"'),
    (TokenType.SINGLE_QUOTE, r"\'"),
    (TokenType.IDENTIFIER, r"[A-Za-z_]\w*"),
    (TokenType.GAP, r"[ \t]+"),
    (TokenType.NEWLINE, r"\n"),
    (TokenType.MISMATCH, r"."),
)
