from enum import Enum, auto

class TokenType(Enum):
    # Keywords
    LET = auto()                # "let"
    RETURN = auto()             # "return"
    IF = auto()                 # "if"
    ELSE = auto()               # "else"
    WHILE = auto()              # "while"
    RANGE = auto()              # "range"
    EACH = auto()               # "each"
    FUNC = auto()               # "func"
    ECHO = auto()               # "echo"
    IN = auto()                 # "in"
    TO = auto()                 # "to"
    BY = auto()                 # "by"

    # Identifiers
    IDENTIFIER = auto()

    # Delimiters
    LPAREN = auto()             # "("
    RPAREN = auto()             # ")"
    LBRACE = auto()             # "{"
    RBRACE = auto()             # "}"
    LBRACKET = auto()           # "["
    RBRACKET = auto()           # "]"
    COMMA = auto()              # ","
    SEMICOLON = auto()          # ";"
    ARROW = auto()              # ">>"
    RETURN_ARROW = auto()       # "->"

    # Primitives
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    NULL = auto()

    # Operators
    # Arithmetic
    PLUS = auto()               # "+"
    MINUS = auto()              # "-"
    MULTIPLY = auto()           # "*"
    DIVIDE = auto()             # "/"

    # Assignment
    ASSIGN = auto()             # "="
    PLUS_ASSIGN = auto()        # "+="
    MINUS_ASSIGN = auto()       # "-="
    MULTIPLY_ASSIGN = auto()    # "*="
    DIVIDE_ASSIGN = auto()      # "/="

    # Logical
    LOGICAL_AND = auto()        # "&&"
    LOGICAL_OR = auto()         # "||"
    LOGICAL_NOT = auto()        # "!"

    # Comparitive
    EQUAL = auto()              # "=="
    NOT_EQUAL = auto()          # "!="
    LT = auto()                 # "<"
    GT = auto()                 # ">"
    LTE = auto()                # "<="
    GTE = auto()                # ">="

    # Unary
    INCREMENT = auto()          # "++"
    DECREMENT = auto()          # "--"

    # String tokens
    DOUBLE_QUOTE = auto()       # '"'
    SINGLE_QUOTE = auto()       # '\''
    STRING = auto()

    # Comments
    EOL_COMMENT = auto()        # "// ... \n"
    DELIMITED_COMMENT = auto()  # "/* ... */"

    # End of file
    EOF = auto()

    # Other
    SKIP = auto()
    NEWLINE = auto()
    MISMATCH = auto()
'''
    Note: The following regular expressions are used to match tokens in the lexer.
    The order of the tokens in the spec is critical, as the lexer will yield the
    first token it matches. For instance, if the input is "+=", the lexer will yield
    a PLUS_ASSIGN token, not a PLUS token followed by a ASSIGN token.
'''
spec = (
    (TokenType.LET, r'\blet\b'),
    (TokenType.RETURN, r'\breturn\b'),
    (TokenType.IF, r'\bif\b'),
    (TokenType.ELSE, r'\belse\b'),
    (TokenType.WHILE, r'\bwhile\b'),
    (TokenType.RANGE, r'\brange\b'),
    (TokenType.EACH, r'\beach\b'),
    (TokenType.FUNC, r'\bfunc\b'),
    (TokenType.ECHO, r'\becho\b'),
    (TokenType.IN, r'\bin\b'),
    (TokenType.TO, r'\bto\b'),
    (TokenType.BY, r'\bby\b'),

    (TokenType.LPAREN, r'\('),
    (TokenType.RPAREN, r'\)'),
    (TokenType.LBRACE, r'\{'),
    (TokenType.RBRACE, r'\}'),
    (TokenType.LBRACKET, r'\['),
    (TokenType.RBRACKET, r'\]'),
    (TokenType.COMMA, r','),
    (TokenType.SEMICOLON, r';'),
    (TokenType.ARROW, r'>>'),
    (TokenType.RETURN_ARROW, r'->'),

    (TokenType.EOL_COMMENT, r'//.*\n'),
    (TokenType.DELIMITED_COMMENT, r'/\*[\s\S]*?(?:\*/|$)'),

    (TokenType.LOGICAL_AND, r'&&'),
    (TokenType.LOGICAL_OR, r'\|\|'),
    (TokenType.LOGICAL_NOT, r'!'),

    (TokenType.INCREMENT, r'\+\+'),
    (TokenType.DECREMENT, r'--'),

    (TokenType.ASSIGN, r'='),
    (TokenType.PLUS_ASSIGN, r'\+='),
    (TokenType.MINUS_ASSIGN, r'-='),
    (TokenType.MULTIPLY_ASSIGN, r'\*='),
    (TokenType.DIVIDE_ASSIGN, r'/='),

    (TokenType.EQUAL, r'=='),
    (TokenType.NOT_EQUAL, r'!='),
    (TokenType.LT, r'<'),
    (TokenType.GT, r'>'),
    (TokenType.LTE, r'<='),
    (TokenType.GTE, r'>='),

    (TokenType.PLUS, r'\+'),
    (TokenType.MINUS, r'-'),
    (TokenType.MULTIPLY, r'\*'),
    (TokenType.DIVIDE, r'/'),

    (TokenType.BOOL, r'\btrue\b|\bfalse\b'),
    (TokenType.NULL, r'\bnull\b'),
    (TokenType.FLOAT, r'\d+\.\d+'),
    (TokenType.INT, r'\d+'),

    (TokenType.DOUBLE_QUOTE, r'"'),
    (TokenType.SINGLE_QUOTE, r'\''),

    (TokenType.IDENTIFIER, r'[A-Za-z_]\w*'),

    (TokenType.SKIP, r'[ \t]+'),
    (TokenType.NEWLINE, r'\n'),
    (TokenType.MISMATCH, r'.')
)
