import sys
import os
from lexercorvus import tokenize
from parsercorvus import Parser
from evaluatorcorvus import Evaluator, Environment
from errors import CorvusError, explain_error
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

def run_file(filepath: str, ai_fix: bool = False):
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
        evaluator.current_file_path = filepath
        evaluator.evaluate(ast)

    except CorvusError as e:
        e.print_formatted(filepath, code, ai_fix=ai_fix)
        sys.exit(1)

    except Exception as e:
        print(f"[Corvus Internal Bug]: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        start_repl()
        return

    # Check for --explain / -e
    if sys.argv[1] in ("--explain", "-e"):
        code = sys.argv[2] if len(sys.argv) > 2 else "all"
        explain_error(code)
        sys.exit(0)

    arg1 = sys.argv[1]

    if arg1 in ("--repl", "-r"):
        start_repl()
    elif arg1 in ("--check", "-c"):
        if len(sys.argv) < 3:
            print("Usage: python Corvus.py --check <filename.crv>")
            sys.exit(1)
        check_syntax(sys.argv[2])
    elif arg1 in ("--help", "-h"):
        print("Corvus Language Launcher v4.3.0")
        print("Usage:")
        print("  python Corvus.py                         Launch interactive REPL")
        print("  python Corvus.py <file.crv>              Execute Corvus source file")
        print("  python Corvus.py <file.crv> --ai-fix     Execute with AI-grade diagnostic solutions")
        print("  python Corvus.py --explain [CODE]        Explain an error code (or all)")
        print("  python Corvus.py --check <file.crv>      Syntax check / linter mode")
        print("  python Corvus.py --repl                  Launch interactive REPL")
    else:
        # Check for --ai-fix flag anywhere in args
        ai_fix = "--ai-fix" in sys.argv
        args_filtered = [a for a in sys.argv[1:] if a != "--ai-fix"]
        if args_filtered:
            run_file(args_filtered[0], ai_fix=ai_fix)
        else:
            start_repl()

if __name__ == "__main__":
    main()
