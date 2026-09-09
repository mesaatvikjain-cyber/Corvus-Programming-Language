import sys
import os
from lexercorvus import tokenize
from parsercorvus import Parser
from evaluatorcorvus import Evaluator, Environment
from errors import CorvusError
from repl import start_repl

def check_syntax(filepath: str):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    try:
        tokens = tokenize(code)
        parser = Parser(tokens)
        parser.parse()
        print(f"[Corvus Linter]: Syntax check passed for '{filepath}'.")
        sys.exit(0)
    except CorvusError as e:
        e.print_formatted(filepath, code)
        sys.exit(1)
    except Exception as e:
        print(f"[Corvus Syntax Error]: {e}", file=sys.stderr)
        sys.exit(1)

def run_file(filepath: str):
    if not filepath.endswith(".crv"):
        print(f"Error: File '{filepath}' must have a .crv extension.")
        sys.exit(1)

    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    try:
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()

        global_env = Environment()
        evaluator = Evaluator(global_env)
        evaluator.evaluate(ast)

    except CorvusError as e:
        e.print_formatted(filepath, code)
        sys.exit(1)

    except Exception as e:
        print(f"[Corvus Internal Bug]: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        start_repl()
        return

    arg1 = sys.argv[1]

    if arg1 in ("--repl", "-r"):
        start_repl()
    elif arg1 in ("--check", "-c"):
        if len(sys.argv) < 3:
            print("Usage: python Corvus.py --check <filename.crv>")
            sys.exit(1)
        check_syntax(sys.argv[2])
    elif arg1 in ("--help", "-h"):
        print("Corvus Language Launcher v4.0.0")
        print("Usage:")
        print("  python Corvus.py                    Launch interactive REPL")
        print("  python Corvus.py <filename.crv>     Execute Corvus source file")
        print("  python Corvus.py --repl             Launch interactive REPL")
        print("  python Corvus.py --check <file.crv> Syntax check / linter mode")
    else:
        run_file(arg1)

if __name__ == "__main__":
    main()
