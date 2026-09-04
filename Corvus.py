import sys
import os
from lexercorvus import tokenize
from parsercorvus import Parser
from evaluatorcorvus import Evaluator, Environment
from errors import CorvusError

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
        # Display our clean developer-friendly diagnostic
        e.print_formatted(filepath, code)
        sys.exit(1)

    except Exception as e:
        # Catch-all for any unhandled internal crashes
        print(f"[Corvus Internal Bug]: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python corvus.py <filename.crv>")
        sys.exit(1)
    run_file(sys.argv[1])

if __name__ == "__main__":
    main()