# Cirrus Design Philosophy

## Introduction
Cirrus is designed to be a readable and intuitive programming language inspired by the most useful features of modern high-level languages. It features strong and static typing, curly-brace syntax for block delimiters, functional programming constructs, and a clean syntax for defining functions and chaining operations.

## Development Roadmap
### Phase 1: Initial Implementation
- Develop the lexer to tokenise the source code.
- Implement the parser to construct the AST.

### Phase 2: Semantic Analysis
- Implement type checking and scope management.

### Phase 3: Code Generation
- Develop the code generator and integrate with LLVM.

### Phase 4: Runtime Environment
- Build the runtime environment and implement memory management.

### Phase 5: Standard Library
- Expand the standard library with more built-in functions and utilities.

### Phase 6: Optimisation
- Optimise the language implementation for performance.

## Language Syntax
### Variable Declarations
```
let x = 10;
```

### Function Definitions
```
func add = [a, b] >> {
    return a + b;
}
```

### Array Methods and Chaining
```
let numbers = [1, 2, 3, 4, 5];
let result = numbers
    | map(x >> x * 2)
    | filter(x >> x > 5)
    | reduce((acc, x) >> acc + x, 0);
```

### Conditional Statements
```
if x > 10 {
    return "Greater than 10";
} else {
    return "Less than or equal to 10";
}
```

### Loops
```
// Each loop
each element in numbers {
    echo element;
}

// Range loop
range i in 0 to 10 {
    echo i;
}

// While loop
while x < 10 {
    x++;
}
```

## Design Considerations
### Lexer
The lexer scans the source code and converts it into a stream of tokens, each representing a basic language construct like keywords, identifiers, literals, and operators.

### Parser
The parser takes the stream of tokens from the lexer and constructs an Abstract Syntax Tree (AST), representing the hierarchical structure of the program.

### Semantic Analyser
The semantic analyser checks the AST for semantic errors, such as type mismatches and scope violations, ensuring that the program is meaningful and correctly typed.

### Code Generator
The code generator translates the AST into intermediate code or directly into machine code, leveraging LLVM for optimisations and target-specific code generation.

### Runtime Environment
The runtime environment manages the execution of the program, including memory management, garbage collection, and the execution of built-in functions.

## Project Structure
### Overview
The project is organised into several directories, each responsible for a different component of the language implementation.

### Details
- **src/**: Contains the source code.
  - **lexer/**: Lexer implementation.
  - **parser/**: Parser implementation.
  - **ast/**: AST nodes.
- **tests/**: Unit tests for each component.
- **examples/**: Example programs written in the language.
- **scripts/**: Helper scripts for building, testing, and running the project.

### Notes
- Currently, cirrus files are designated with the `.crs` extension, though this may change in the future.
- Whilst the code is written using American English by convention, comments and documentation may be written in British English.