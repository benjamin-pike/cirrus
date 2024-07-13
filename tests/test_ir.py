# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false

import pytest
from llvmlite import ir, binding as llvm
from ctypes import CFUNCTYPE, c_int

from frontend.ir.generator import IRGenerator
from frontend.lexer.lexer import Lexer
from frontend.parser.parser import Parser
from frontend.semantic.analyzer import SemanticAnalyzer

Capfd = pytest.CaptureFixture[str]


def generate(code: str) -> ir.Module:
    lexer = Lexer(code)
    ast = Parser(list(lexer.tokenize())).parse()
    SemanticAnalyzer().analyze(ast)

    return IRGenerator().generate_program(ast)


def execute(ir_code: ir.Module) -> None:
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()

    llvm_module = llvm.parse_assembly(str(ir_code))
    llvm_module.verify()

    with llvm.create_mcjit_compiler(llvm_module, target_machine) as engine:
        engine.finalize_object()
        engine.run_static_constructors()
        func_addr = engine.get_function_address("main")
        func = CFUNCTYPE(c_int)(func_addr)
        func()


def check(capfd: Capfd):
    def compare(code: str, expected_output: str) -> None:
        execute(generate(code))
        out, _ = capfd.readouterr()
        assert out.strip() == expected_output

    return compare


# Variables and Functions
def test_variable_declaration(capfd: Capfd) -> None:
    code = """
        int a = 10;
        echo a;
    """
    check(capfd)(code, "10")


def test_variable_reassignment(capfd: Capfd) -> None:
    code = """
        int a = 10;
        echo a + 20;
    """
    check(capfd)(code, "30")


def test_simple_function(capfd: Capfd) -> None:
    code = """
        func concat -> str = [str a, str b] >> {
            return a + b;
        }
        
        echo concat("Hello ", "World");
    """
    check(capfd)(code, "Hello World")


def test_complex_function(capfd: Capfd) -> None:
    code = """
        func math -> int = [func<int, [int x, int y]> f, int a, int b] >> {
            return f(a, b);
        }
        
        func add -> int = [int x, int y] >> {
            return x + y;
        }
        
        func multiply -> int = [int x, int y] >> {
            return x * y;
        }
        
        echo math(multiply, math(add, 10, 20), 50);
    """

    check(capfd)(code, "1500")


def test_curried_function(capfd: Capfd) -> None:
    code = """
        func multiply -> int = [int a, int b] >> {
            return a * b;
        }

        func divide -> int = [int a, int b] >> {
            return a / b;
        }

        func getMathFunc -> func<int, [int a, int b]> = [str op] >> {
            if (op == 'mul') {
                return multiply;
            }

            return divide;
        }
        
        echo getMathFunc('div')(getMathFunc('mul')(10, 20), 50);
    """
    check(capfd)(code, "4")


def test_pipe_statement(capfd: Capfd) -> None:
    code = """
        func add -> int = [int a, int b] >> {
            return a + b;
        }
        
        func sub -> int = [int a, int b] >> {
            return a - b;
        }
        
        func mul -> int = [int a, int b] >> {
            return a * b;
        }
        
        func div -> int = [int a, int b] >> {
            return a / b;
        }
        
        int a = 10;
        int b = 20;
        
        echo [add(a, b), sub(a, b)] >> mul >> div(20);
    """
    check(capfd)(code, "-15")


# Arrays
def test_array_declaration(capfd: Capfd) -> None:
    code = """
        int[] numbers = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100];
        echo numbers[2];
    """
    check(capfd)(code, "30")
    
def test_array_methods_simple(capfd: Capfd) -> None:
    code = """
        str[] names = ['Alice', 'Bob', 'Charlie'];
        
        echo names.push('Dave').pop();
        echo names.extract(1);
    """
    
    check(capfd)(code, "Dave\nBob")    

def test_array_methods_complex(capfd: Capfd) -> None:
    code = """
        int[] numbers = [10, 20, 30, 40, 50];
        
        echo numbers.insert(5, 60).pop() * numbers.push(70).extract(1);
    """
    check(capfd)(code, "1200")


def test_nested_array_declaration(capfd: Capfd) -> None:
    code = """
        int[][] matrix = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ];
        
        echo matrix[1][2];
    """
    check(capfd)(code, "6")


def test_nested_array_methods(capfd: Capfd) -> None:
    code = """
        int[][] matrix = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ];
        
        echo matrix[1].insert(2, 7).pop() * matrix[2].push(10).extract(1);
    """
    check(capfd)(code, "48")


# Control Flow Statements
def test_if_statement(capfd: Capfd) -> None:
    code = """
        func check -> void = [int a] >> {
            if (a == 10) {
                a = a - 6;

                if (a > 5) {
                    echo a;
                } else {
                    echo "a is less than 5";
                }
            }
            
            return;
        }
        
        check(10);
    """
    check(capfd)(code, "a is less than 5")


def test_while_statement(capfd: Capfd) -> None:
    code = """
        int a = 10;
       
        while (a > 0) {
            echo a;
            a--;
            
            if (a == 5) {
                echo "midway";
            }
        }
    """
    check(capfd)(code, "10\n9\n8\n7\n6\nmidway\n5\n4\n3\n2\n1")


def test_each_statement(capfd: Capfd) -> None:
    code = """
        str[] names = ["Alice", "Bob", "Charlie", "Alice"];
        
        each (name in names) {
            echo name;
        }
    """
    check(capfd)(code, "Alice\nBob\nCharlie\nAlice")


def test_range_statement(capfd: Capfd) -> None:
    code = """
        range (i in 0 to 10 by 2) {
            echo i;
        }
    """
    check(capfd)(code, "0\n2\n4\n6\n8")


def test_halt_statement(capfd: Capfd) -> None:
    code = """
        str[] names = ["Alice", "Bob", "Charlie"];
        
        range (i in 0 to 5) {
            bool terminate = false;
            
            each (name in names) {                
                if (name == "Bob" && i == 2) {
                    terminate = true;
                    halt;
                }
                
                echo name;
            }
            
            if (terminate) {
                halt;
            }
        }
    """

    check(capfd)(code, "Alice\nBob\nCharlie\nAlice\nBob\nCharlie\nAlice")


def test_skip_statement(capfd: Capfd) -> None:
    code = """
        str[] names = ["Alice", "Bob", "Charlie"];
        
        range (i in 0 to 5) {
            if (i > 3) {
                skip;
            }

            each (name in names) {
                if (name == "Bob" && i == 2) {
                    skip;
                }
                
                echo name;
            }
        }
    """
    check(capfd)(
        code,
        "Alice\nBob\nCharlie\nAlice\nBob\nCharlie\nAlice\nCharlie\nAlice\nBob\nCharlie",
    )

# Hash Types
def test_set_declaration(capfd: Capfd) -> None:
    code = """
        str{} names = {'Alice', 'Bob', 'Charlie'};
    """
    check(capfd)(code, "")