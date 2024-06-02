# Grammar of Cirrus

### Keywords
```ebnf
KEYWORD = "let" | "return"
```


### Identifiers
```ebnf
IDENTIFIER = LETTER , { LETTER | DIGIT | "_" };
LETTER = "A" | "B" | ... | "Z" | "a" | "b" | ... | "z";
DIGIT = "0" | "1" | ... | "9";
```


### Primitive Types
```ebnf
INT = DIGIT , { DIGIT };
FLOAT = DIGIT , { DIGIT } , "." , DIGIT , { DIGIT };
NUMBER = INT | FLOAT;
BOOL = "true" | "false";

ASCII_CHAR = 'a' | 'b' | 'c' | 'd' | 'e' | 'f' | 'g' | 'h' | 'i' | 'j' | 'k' | 'l' | 
             'm' | 'n' | 'o' | 'p' | 'q' | 'r' | 's' | 't' | 'u' | 'v' | 'w' | 'x' | 
             'y' | 'z' | 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'I' | 'J' | 
             'K' | 'L' | 'M' | 'N' | 'O' | 'P' | 'Q' | 'R' | 'S' | 'T' | 'U' | 'V' | 
             'W' | 'X' | 'Y' | 'Z' | '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | 
             '8' | '9' | ' ' | '!' | '#' | '$' | '%' | '&' | '(' | ')' | '*' | '+' | 
             ',' | '-' | '.' | '/' | ':' | ';' | '<' | '=' | '>' | '?' | '@' | '[' | 
             '\\' | ']' | '^' | '_' | '`' | '{' | '|' | '}' | '~' | '\'' | '\"';
ESCAPE_CHAR = '\\' , ( '\'' | '\"' | '\\' );
STRING = { ASCII_CHAR | ESCAPE_CHAR };
```

### Operators
```ebnf
OPERATORS = 
    | LOGICAL_OPERATORS 
    | MATHEMATICAL_OPERATORS 
    | RELATIONAL_OPERATORS 
    | ASSIGNMENT_OPERATORS 
    | INCREMENT_DECREMENT_OPERATORS;

LOGICAL_OPERATORS = "&&" | "||" | "!";
MATHEMATICAL_OPERATORS = "+" | "-" | "*" | "/";
RELATIONAL_OPERATORS = "==" | "!=" | "<" | ">" | "<=" | ">=" ;
ASSIGNMENT_OPERATORS = "=" | "+=" | "-=" | "*=" | "/=";
INCREMENT_DECREMENT_OPERATORS = "++" | "--";
```

### Expressions
```ebnf
EXPRESSION = 
    | ASSIGNMENT_EXPRESSION 
    | FUNC_DEFINITION 
    | ARITHMETIC_EXPRESSION
    | COMPARISION_EXPRESSION;

ASSIGNMENT_EXPRESSION = "let" , IDENTIFIER , "=" , EXPRESSION , ";";

FUNC_DEFINITION = "(" , [ PARAM_LIST ] , ")" , "->" , TYPE , "=>" , "{" , { STATEMENT } , "}";
PARAM_LIST = PARAM , { "," , PARAM };
PARAM = IDENTIFIER , ":" , TYPE;
TYPE = "int" | "float" | "string" | "bool" | IDENTIFIER;

ARITHMETIC_EXPRESSION = TERM , { ("+" | "-") , TERM };
TERM = FACTOR , { ("*" | "/") , FACTOR };
FACTOR = INT | FLOAT | IDENTIFIER | "(" , EXPRESSION , ")";
COMPARISION_EXPRESSION = EXPRESSION , ( ">" | "<" | "==" | "!=" ) , EXPRESSION;
```

### Statements
```ebnf
STATEMENT = 
    | ASSIGNMENT_STATEMENT 
    | RETURN_STATEMENT 
    | CONDITIONAL_STATEMENT 
    | LOOP_STATEMENT
    | FUNC_CALL_STATEMENT;

ASSIGNMENT_STATEMENT = ASSIGNMENT_EXPRESSION;
RETURN_STATEMENT = "return" , EXPRESSION , ";";
CONDITIONAL_STATEMENT = "if", EXPRESSION , "{" , { STATEMENT } , "}" , [ "else" , "{" , { STATEMENT } , "}" ];
LOOP_STATEMENT = "while" , EXPRESSION , {" , { STATEMENT } , "}";
FUNC_CALL_STATEMENT = IDENTIFIER , "(" , [ ARG_LIST ] , ")" , ";";
ARG_LIST = EXPRESSION , { "," , EXPRESSION };
```