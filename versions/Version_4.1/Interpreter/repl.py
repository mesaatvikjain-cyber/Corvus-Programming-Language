# Corvus v4.0 Interactive REPL Shell Engine
# Features: Multi-line parsing, Tab Auto-Completion, Environment State Directives, and Resilient Tracebacks

import sys
import os
from lexercorvus import tokenize
from parsercorvus import Parser
from evaluatorcorvus import Evaluator, Environment
from errors import CorvusError

# Try setting up readline auto-completion if available
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

CORVUS_KEYWORDS = [
    "set", "var", "const", "mk", "func", "givout", "if", "else", 
    "while", "for", "try", "cls", "struct", "async", "await", "import"
]

CORVUS_BUILTINS = [
    "print", "len", "type", "abs", "max", "min", "pow", 
    "factorial", "clamp", "sqrt_approx", "read_all", "write_all"
]

class CorvusCompleter:
    def __init__(self, env: Environment):
        self.env = env

    def complete(self, text, state):
        symbols = set(CORVUS_KEYWORDS + CORVUS_BUILTINS)
        if hasattr(self.env, 'variables'):
            symbols.update(self.env.variables.keys())
        if hasattr(self.env, 'functions'):
            symbols.update(self.env.functions.keys())

        matches = [s for s in symbols if s.startswith(text)]
        if state < len(matches):
            return matches[state]
        return None

def start_repl():
    print("=========================================================")
    print("  Corvus Interactive REPL Shell v4.0.0 (Release 4.0)")
    print("  Type .help for directives, .exit or Ctrl+C to quit.")
    print("=========================================================\n")

    global_env = Environment()
    evaluator = Evaluator(global_env)

    if READLINE_AVAILABLE:
        completer = CorvusCompleter(global_env)
        readline.set_completer(completer.complete)
        readline.parse_and_bind("tab: complete")

    buffer = ""
    multiline = False

    while True:
        try:
            prompt = "......> " if multiline else "corvus> "
            try:
                line = input(prompt)
            except EOFError:
                print("\nExiting Corvus REPL.")
                break

            stripped = line.strip()

            # Process REPL directives
            if not multiline and stripped.startswith("."):
                cmd = stripped.lower()
                if cmd in (".exit", ".quit"):
                    print("Exiting Corvus REPL.")
                    break
                elif cmd == ".help":
                    print("\nCorvus REPL Directives:")
                    print("  .help    - Show this help manual")
                    print("  .vars    - Display currently defined variables & values")
                    print("  .funcs   - Display currently defined functions")
                    print("  .clear   - Clear terminal screen")
                    print("  .reset   - Reset environment state")
                    print("  .exit    - Exit interactive REPL session\n")
                    continue
                elif cmd == ".vars":
                    print("\n--- Defined Variables ---")
                    if hasattr(global_env, 'variables') and global_env.variables:
                        for k, v in global_env.variables.items():
                            print(f"  {k} = {v}")
                    else:
                        print("  (no variables declared)")
                    print()
                    continue
                elif cmd == ".funcs":
                    print("\n--- Defined Functions ---")
                    if hasattr(global_env, 'functions') and global_env.functions:
                        for f_name in global_env.functions.keys():
                            print(f"  func {f_name}(...)")
                    else:
                        print("  (no functions declared)")
                    print()
                    continue
                elif cmd == ".clear":
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                elif cmd == ".reset":
                    global_env = Environment()
                    evaluator = Evaluator(global_env)
                    print("Environment reset to clean state.\n")
                    continue
                else:
                    print(f"Unknown REPL directive '{stripped}'. Type .help for available commands.")
                    continue

            buffer += line + "\n"

            # Check unclosed block braces
            open_braces = buffer.count("{") - buffer.count("}")
            open_parens = buffer.count("(") - buffer.count(")")

            if open_braces > 0 or open_parens > 0:
                multiline = True
                continue

            multiline = False
            code_to_eval = buffer
            buffer = ""

            if not code_to_eval.strip():
                continue

            try:
                tokens = tokenize(code_to_eval)
                parser = Parser(tokens)
                ast = parser.parse()
                res = evaluator.evaluate(ast)
                if res is not None:
                    print(f"=> {res}")
            except CorvusError as err:
                err.print_formatted("<repl>", code_to_eval)
            except Exception as ex:
                print(f"[REPL Runtime Exception]: {ex}", file=sys.stderr)

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt (type .exit to quit)")
            buffer = ""
            multiline = False

if __name__ == "__main__":
    start_repl()
