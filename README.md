# Cirrus

## Introduction
Cirrus is designed to be a readable and intuitive programming language inspired by the most useful features of modern high-level languages. It features strong and static typing, curly-brace syntax for block delimiters, functional programming constructs, and a clean syntax for defining functions and chaining operations.

## Setup

### Cloning the Repository
First, you need to clone the repository to your local machine. Open your terminal and run the following command:
```
git clone https://github.com/benjamin-pike/cirrus.git
cd cirrus
```

### Running the Setup Script
To ensure the development environment is configured correctly, you should run the project setup script. To do so, execute the following command in your terminal:
```
python setup.py
```

### What the Setup Script Does

1. **Validates Python Version**:
   - Ensures that you are using Python 3.10 or later. I recommend using `pyenv` to manage your Python versions.

2. **Installs Required Packages**:
   - Installs all necessary packages specified in the `requirements.txt` file using pip.

3. **Installs Pre-commit Hook**:
   - Installs the `pre-commit` package and sets up the pre-commit hook to ensure code quality checks before committing changes.

4. **Adds Source Directory to System Path**:
   - Adds the `src` directory to the system path, allowing you to run the project from the command line without path issues.

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
int x = 10;
str y = 'Hello, World!';
bool z = true;
```

### Function Definitions
```
func add -> int = [int a, int b] >> {
    return a + b;
}
```

### Templates and Entities
```
template User {
    str name;
    int age;
    User[] followers;

    func poke -> void = [] >> {
        echo 'Poked ' + name;
    } 
}

entity user = User{
    name: 'James',
    age: 25,
    followers: [
        User{name: 'Alice', age: 30, followers: []},
        User{name: 'Bob', age: 28, followers: []}
    ]
};

user.poke();
```

### Array Methods and Chaining
```
int[] numbers = [1, 2, 3, 4, 5];
int result = numbers >> map(double) >> reduce(add)
```

### Conditional Statements
```
if (x > 10) {
    echo 'Greater than 10';
} else {
    echo 'Less than or equal to 10';
}
```

### Loops
```
// Each loop
each (element in numbers) {
    echo element;
}

// Range loop
range (i in 0 to 10) {
    echo i;
}

// While loop
while (x < 10) {
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
  - **parser/**: Parser components.
  - **ast/**: AST nodes.
  - **semantic/**: Semantic analyzer components.
- **tests/**: Unit tests for each component.
- **examples/**: Example programs written in the language.
- **scripts/**: Helper scripts for building, testing, and running the project.

### Notes
- Currently, cirrus files are designated with the `.crs` extension, though this may change in the future.
- Whilst the code is written using American English by convention, comments and documentation may be written in British English.
