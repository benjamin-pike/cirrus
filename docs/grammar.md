# Grammar of Cirrus

### Keywords
```ebnf
KEYWORD = 'return' | 'if' | 'else' | 'while' | 'range' | 'each' | 'func' |
          'echo' |'in' | 'to' | 'by' | 'halt' | 'skip' | 'int' | 'float' |
          'bool' | 'string' | 'null' | 'infer' | 'void' | 'true' | 'false' |
          'template' | 'entity' 

```

### Identifiers
```ebnf
IDENTIFIER = LETTER , { LETTER | DIGIT | '_' };
LETTER = 'A' | 'B' | ... | 'Z' | 'a' | 'b' | ... | 'z';
DIGIT = '0' | '1' | ... | '9';
```

### Primitive Types
```ebnf
INT = DIGIT , { DIGIT };
FLOAT = DIGIT , { DIGIT } , '.' , DIGIT , { DIGIT };
NUMBER = INT | FLOAT;
BOOL = 'true' | 'false';

ASCII_CHAR = 'a' | 'b' | 'c' | 'd' | 'e' | 'f' | 'g' | 'h' | 'i' | 'j' | 'k' | 'l' |
             'm' | 'n' | 'o' | 'p' | 'q' | 'r' | 's' | 't' | 'u' | 'v' | 'w' | 'x' |
             'y' | 'z' | 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'I' | 'J' |
             'K' | 'L' | 'M' | 'N' | 'O' | 'P' | 'Q' | 'R' | 'S' | 'T' | 'U' | 'V' |
             'W' | 'X' | 'Y' | 'Z' | '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' |
             '8' | '9' | ' ' | '!' | '#' | '$' | '%' | '&' | '(' | ')' | '*' | '+' |
             ',' | '-' | '.' | '/' | ':' | ';' | '<' | '=' | '>' | '?' | '@' | '[' |
             '\\' | ']' | '^' | '_' | '`' | '{' | '|' | '}' | '~' | '\'' | '"';
ESCAPE_CHAR = '\\' , ( '\'' | '"' | '\\' );
STR = { ASCII_CHAR | ESCAPE_CHAR };
```

### Collection Types
```ebnf
ARRAY = '[' , [ EXPRESSION , { ',' , EXPRESSION } ] , ']';
SET = '{' , [ EXPRESSION , { ',' , EXPRESSION } ] , '}';
MAP = '{' , [ EXPRESSION , ':' , EXPRESSION , { ',' , EXPRESSION , ':' , EXPRESSION } ] , '}';
```

### Object Types
```ebnf
TEMPLATE_DECLARATION = 'template' , IDENTIFIER , '{' , { ATTRIBUTE_DECLARATION, FUNCTION_DECLARATION } , '}';
ENTITY = 'entity' , IDENTIFIER, =, ENTITY_LITERAL;
ATTRIBUTE_DECLARATION = TYPE , IDENTIFIER , ';';
ENTITY_LITERAL = IDENTIFIER, '{' , { IDENTIFIER , ':' , EXPRESSION , ',' } , '}';
```

### Operators
```ebnf
OPERATORS =
    | LOGICAL_OPERATORS
    | MATHEMATICAL_OPERATORS
    | RELATIONAL_OPERATORS
    | ASSIGNMENT_OPERATORS
    | INCREMENT_DECREMENT_OPERATORS;

LOGICAL_OPERATORS = '&&' | '||' | '!';
MATHEMATICAL_OPERATORS = '+' | '-' | '*' | '/';
RELATIONAL_OPERATORS = '==' | '!=' | '<' | '>' | '<=' | '>=' ;
ASSIGNMENT_OPERATORS = '=' | '+=' | '-=' | '*=' | '/=';
INCREMENT_DECREMENT_OPERATORS = '++' | '--';
```

### Expressions
```ebnf
EXPRESSION =
    | ASSIGNMENT_EXPRESSION
    | FUNC_DEFINITION
    | ARITHMETIC_EXPRESSION
    | COMPARISON_EXPRESSION
    | LOGICAL_EXPRESSION
    | UNARY_EXPRESSION
    | FUNCTION_CALL_EXPRESSION
    | METHOD_CALL_EXPRESSION
    | PIPE_EXPRESSION
    | LITERAL;

ASSIGNMENT_EXPRESSION = IDENTIFIER , ASSIGNMENT_OPERATORS , EXPRESSION , ';';
FUNC_DEFINITION = 'func' , IDENTIFIER , '->' , TYPE , '=' , '[' , [ PARAM_LIST ] , ']' , '>>' , '{' , { STATEMENT } , '}';
PARAM_LIST = PARAM , { ',' , PARAM };
PARAM = TYPE , IDENTIFIER;

TYPE = HASHABLE_TYPE | 'void' | 'infer' | ARRAY_TYPE | MAP_TYPE;
HASHABLE_TYPE = 'int' | 'float' | 'string' | 'bool' | 'null' | SET_TYPE
ARRAY_TYPE = TYPE '[]';
SET_TYPE = HASHABLE_TYPE '{}';
MAP_TYPE = TYPE '{' HASHABLE_TYPE '}';

ARITHMETIC_EXPRESSION = TERM , { ('+' | '-') , TERM };
TERM = FACTOR , { ('*' | '/') , FACTOR };
FACTOR = NUMBER | IDENTIFIER | '(' , EXPRESSION , ')';
COMPARISON_EXPRESSION = EXPRESSION , RELATIONAL_OPERATORS , EXPRESSION;
LOGICAL_EXPRESSION = EXPRESSION , LOGICAL_OPERATORS , EXPRESSION;
UNARY_EXPRESSION = INCREMENT_DECREMENT_OPERATORS , IDENTIFIER | '!' , IDENTIFIER;
FUNCTION_CALL_EXPRESSION = IDENTIFIER , '(' , [ ARG_LIST ] , ')';
ANONYMOUS_FUNCTION = 'func', '[', [ PARAM_LIST ], ']', '>>', '{', { STATEMENT }, '}';
METHOD_CALL_EXPRESSION = IDENTIFIER , '.' , IDENTIFIER , '(' , [ ARG_LIST ] , ')';
ARG_LIST = EXPRESSION , { ',' , EXPRESSION };
PIPE_EXPRESSION =  '[' , ARG_LIST , ']' , '>>' , PIPE_FUNCTION , { '>>' , PIPE_FUNCTION };
PIPE_FUNCTION = IDENTIFIER , [ '(' , [ FUNC_ARG_LIST ] , ')' ];

LITERAL = NUMBER | STR | BOOL | ARRAY | SET | MAP | 'null' | ENTITY_LITERAL | ANONYMOUS_FUNCTION;
```

### Statements
```ebnf
STATEMENT =
    | VARIABLE_DECLARATION
    | RETURN_STATEMENT
    | CONDITIONAL_STATEMENT
    | LOOP_STATEMENT
    | EACH_STATEMENT
    | RANGE_STATEMENT
    | HALT_STATEMENT
    | SKIP_STATEMENT
    | ECHO_STATEMENT
    | EXPRESSION_STATEMENT
    | BLOCK_STATEMENT;

VARIABLE_DECLARATION = TYPE , IDENTIFIER , '=' , EXPRESSION , ';';
RETURN_STATEMENT = 'return' , EXPRESSION , ';';
CONDITIONAL_STATEMENT = 'if' , EXPRESSION , '{' , { STATEMENT } , '}' , [ 'else' , '{' , { STATEMENT } , '}' ];
LOOP_STATEMENT = 'while' , '(' , EXPRESSION , ')' , '{' , { STATEMENT } , '}';
EACH_STATEMENT = 'each' , IDENTIFIER , 'in' , EXPRESSION , '{' , { STATEMENT } , '}';
RANGE_STATEMENT = 'range' , IDENTIFIER , 'in' , EXPRESSION , 'to' , EXPRESSION , [ 'by' , EXPRESSION ] , '{' , { STATEMENT } , '}';
HALT_STATEMENT = 'halt' , ';';
SKIP_STATEMENT = 'skip' , ';';
ECHO_STATEMENT = 'echo' , STR , ';';
EXPRESSION_STATEMENT = EXPRESSION , ';';
BLOCK_STATEMENT = '{' , { STATEMENT } , '}';
```

### Program
```ebnf
PROGRAM = { STATEMENT };
```
