import os
import sys
import random
import time
import argparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(root, 'Interpreter'))

try:
    import lexercorvus
    import parsercorvus
    import evaluatorcorvus
    import compiler_vm
    import bytecode
    from errors import CorvusError
except ImportError as e:
    print(f"[ERROR] Could not import Corvus engine components: {e}")
    sys.exit(1)

CORVUS_SNIPPETS = [
    "set int x = 42\n",
    "set str name = \"Corvus\"\n",
    "const MAX = 100\n",
    "if x > 10 [ givout x ]\n",
    "while (i < 5) [ set i = i + 1 ]\n",
    "for item in [1, 2, 3] [ log(item) ]\n",
    "func calc(a, b) [ givout a * b ]\n",
    "class Item [ func init(v) [ set this.v = v ] ]\n",
    "set C = [[1, 2]] @ [[3], [4]]\n",
    "set grade = x >= 90 ? \"A\" : \"B\"\n",
    "set msg = f\"Value: {x}\"\n",
    "brk\n",
    "con\n",
    "givout 0\n",
    "match x [ case 1 => log(1) else => log(2) ]\n",
]

CORVUS_MUTATION_TOKENS = [
    "[", "]", "{", "}", "(", ")", ":", ";", ",", "@", "?", "=", "==", "!=",
    "<", ">", "<=", ">=", "+", "-", "*", "/", "%", "|>", "->", "=>",
    "set", "const", "var", "func", "mk", "class", "if", "elsif", "else",
    "while", "for", "in", "brk", "con", "givout", "match", "case", "lambda",
    "f\"", "\"", "'", "\0", "\n", "\t", "\\", "99999999999999999999",
    "-1", "NaN", "null", "undefined", "true", "fal", "this", "self"
]

class CorvusFuzzer:
    def __init__(self, corpus_dir: str = None, crashes_dir: str = None):
        self.corpus_dir = corpus_dir or os.path.join(os.path.dirname(__file__), 'fuzz_corpus')
        self.crashes_dir = crashes_dir or os.path.join(self.corpus_dir, 'crashes')
        os.makedirs(self.crashes_dir, exist_ok=True)
        self.seeds = self._load_seeds()

    def _load_seeds(self) -> list:
        seeds = []
        if os.path.exists(self.corpus_dir):
            for f in os.listdir(self.corpus_dir):
                if f.endswith('.crv'):
                    with open(os.path.join(self.corpus_dir, f), 'r', encoding='utf-8', errors='replace') as fp:
                        seeds.append(fp.read())
        if not seeds:
            seeds = ["set x = 10\nfunc test() [ givout x * 2 ]\n"]
        return seeds

    def generate_random_code(self) -> str:
        mode = random.choice(["mutate_seed", "token_soup", "bracket_bomb", "structural_chaos"])

        if mode == "mutate_seed":
            base = random.choice(self.seeds)
            return self.mutate(base)
        elif mode == "bracket_bomb":
            depth = random.randint(10, 60)
            openers = [random.choice(["[", "{", "(", "[["]) for _ in range(depth)]
            closers = [random.choice(["]", "}", ")", "]]"]) for _ in range(depth)]
            return "".join(openers) + " set x = 1 " + "".join(closers)
        elif mode == "token_soup":
            length = random.randint(5, 40)
            return " ".join(random.choice(CORVUS_MUTATION_TOKENS) for _ in range(length))
        else:
            lines = [random.choice(CORVUS_SNIPPETS) for _ in range(random.randint(2, 5))]
            return self.mutate("".join(lines))

    def mutate(self, text: str) -> str:
        chars = list(text)
        if not chars:
            chars = list("set x = 10")

        mutations = random.randint(1, 6)
        for _ in range(mutations):
            op = random.choice(["insert_token", "delete_char", "swap_char", "replace_token", "duplicate_slice"])
            idx = random.randint(0, len(chars) - 1) if chars else 0

            if op == "insert_token":
                tok = random.choice(CORVUS_MUTATION_TOKENS)
                chars.insert(idx, tok)
            elif op == "delete_char" and len(chars) > 1:
                chars.pop(idx)
            elif op == "swap_char" and idx < len(chars) - 1:
                chars[idx], chars[idx + 1] = chars[idx + 1], chars[idx]
            elif op == "replace_token":
                tok = random.choice(CORVUS_MUTATION_TOKENS)
                chars[idx] = tok
            elif op == "duplicate_slice" and len(chars) > 3:
                start = random.randint(0, len(chars) - 2)
                end = random.randint(start + 1, min(start + 8, len(chars)))
                chars[start:start] = chars[start:end]

        return "".join(chars)

    def test_candidate(self, code: str) -> tuple:
        try:
            tokens = lexercorvus.tokenize(code)
        except CorvusError:
            return True, "Caught cleanly by CorvusError in Lexer", False
        except Exception as e:
            return False, f"UNHANDLED CRASH in Lexer: {type(e).__name__}: {e}", True

        try:
            parser = parsercorvus.Parser(tokens)
            ast = parser.parse()
        except CorvusError:
            return True, "Caught cleanly by CorvusError in Parser", False
        except Exception as e:
            return False, f"UNHANDLED CRASH in Parser: {type(e).__name__}: {e}", True

        try:
            compiler = compiler_vm.BytecodeCompiler("<fuzz>")
            code_obj = compiler.compile(ast)
            serialized = bytecode.serialize(code_obj)
            deserialized = bytecode.deserialize(serialized)
        except (CorvusError, ValueError):
            return True, "Clean rejection in Bytecode pipeline", False
        except Exception as e:
            return False, f"UNHANDLED CRASH in Bytecode Compiler: {type(e).__name__}: {e}", True

        try:
            env = evaluatorcorvus.Environment()
            evaluator = evaluatorcorvus.Evaluator(env)
            evaluator.evaluate(ast)
        except (CorvusError, ValueError):
            return True, "Caught cleanly by CorvusError in Evaluator", False
        except Exception as e:
            return False, f"UNHANDLED CRASH in Evaluator: {type(e).__name__}: {e}", True

        return True, "Executed without error", False

    def run(self, iterations: int = 100, max_time_seconds: float = 30.0) -> dict:
        print(f"=== Starting Corvus Fuzzing Session ({iterations} iterations) ===")
        start_time = time.time()
        crashes = []
        handled_errors = 0
        valid_executions = 0

        for i in range(1, iterations + 1):
            if time.time() - start_time > max_time_seconds:
                print(f"[INFO] Time limit of {max_time_seconds}s reached at iteration {i}.")
                break

            candidate = self.generate_random_code()
            ok, reason, is_crash = self.test_candidate(candidate)

            if is_crash:
                crash_id = f"crash_{int(time.time())}_{i}.crv"
                crash_path = os.path.join(self.crashes_dir, crash_id)
                with open(crash_path, 'w', encoding='utf-8') as f:
                    f.write(candidate)
                crashes.append((crash_id, reason, candidate))
                print(f"  ❌ [{i}/{iterations}] CRASH DETECTED: {reason} (Saved: {crash_id})")
            else:
                if "Executed without error" in reason:
                    valid_executions += 1
                else:
                    handled_errors += 1

            if i % 25 == 0 or i == iterations:
                print(f"  ... Fuzzing progress: {i}/{iterations} tested (Handled: {handled_errors}, Crashes: {len(crashes)})")

        elapsed = time.time() - start_time
        print("\n==================================================")
        print(f"  Corvus Fuzzing Session Completed in {elapsed:.2f}s")
        print(f"  Iterations Tested : {i}")
        print(f"  Handled Cleanly   : {handled_errors}")
        print(f"  Valid Executed    : {valid_executions}")
        print(f"  Crashes / Bugs    : {len(crashes)}")
        print("==================================================")

        return {
            "iterations": i,
            "crashes": crashes,
            "handled": handled_errors,
            "valid": valid_executions,
            "elapsed": elapsed
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corvus Fuzzing & Stress Testing Engine")
    parser.add_argument("--iterations", "-n", type=int, default=100, help="Number of fuzz iterations")
    parser.add_argument("--timeout", "-t", type=float, default=30.0, help="Maximum execution time in seconds")
    args = parser.parse_args()

    fuzzer = CorvusFuzzer()
    results = fuzzer.run(iterations=args.iterations, max_time_seconds=args.timeout)
    if results["crashes"]:
        sys.exit(1)
    sys.exit(0)
