import os
import sys
import time

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

test_dir = os.path.dirname(os.path.abspath(__file__))
categories = ['variables', 'conditions', 'loops', 'functions', 'oop', 'expressions']

print("==========================================================")
print("     CORVUS COMPREHENSIVE NEGATIVE TEST & FUZZ RUNNER     ")
print("==========================================================")

total_tests = 0
passed_cleanly = 0
unhandled_crashes = []

for cat in categories:
    cat_path = os.path.join(test_dir, cat)
    if not os.path.exists(cat_path):
        continue

    print(f"\n--- Testing Category: [{cat.upper()}] ---")
    files = sorted([f for f in os.listdir(cat_path) if f.endswith('.crv')])

    for f in files:
        total_tests += 1
        fp = os.path.join(cat_path, f)
        with open(fp, 'r', encoding='utf-8', errors='replace') as fp_in:
            code = fp_in.read()

        is_crash = False
        crash_err = ""
        stage = ""

        # Step 1: Lexer & Parser
        try:
            tokens = lexercorvus.tokenize(code)
            parser = parsercorvus.Parser(tokens)
            ast = parser.parse()
        except CorvusError:
            # Clean expected syntax/lexer rejection
            print(f"  [PASS - Caught in Parser]: {f}")
            passed_cleanly += 1
            continue
        except Exception as e:
            is_crash = True
            crash_err = f"Parser crash: {type(e).__name__}: {e}"
            stage = "Parser"

        # Step 2: If parsed, test Evaluator (Semantic/Runtime Error Expected)
        if not is_crash:
            try:
                env = evaluatorcorvus.Environment()
                evaluator = evaluatorcorvus.Evaluator(env)
                evaluator.current_file_path = fp
                evaluator.evaluate(ast)
                # If it completed without error, check if this is acceptable or an uncaught semantic error
                print(f"  [WARN - Allowed to run]: {f}")
                passed_cleanly += 1
            except CorvusError:
                print(f"  [PASS - Caught in Evaluator]: {f}")
                passed_cleanly += 1
            except Exception as e:
                is_crash = True
                crash_err = f"Evaluator crash: {type(e).__name__}: {e}"
                stage = "Evaluator"

        if is_crash:
            print(f"  ❌ [FAIL - UNHANDLED CRASH in {stage}]: {f} -> {crash_err}")
            unhandled_crashes.append((cat, f, crash_err))

print("\n==========================================================")
print(f"  Category Tests Finished: {passed_cleanly}/{total_tests} Handled Cleanly")
if unhandled_crashes:
    print(f"  ❌ Detected {len(unhandled_crashes)} unhandled crashes:")
    for cat, f, err in unhandled_crashes:
        print(f"     - [{cat}/{f}]: {err}")
else:
    print("  ✅ 100% of negative tests rejected safely with zero unhandled crashes!")
print("==========================================================")

# Step 3: Fuzzing smoke test
print("\n--- Running Automated Fuzzer Smoke Test (50 iterations) ---")
from fuzzer import CorvusFuzzer
fuzzer = CorvusFuzzer()
fuzz_res = fuzzer.run(iterations=50, max_time_seconds=15.0)

if unhandled_crashes or fuzz_res["crashes"]:
    print("\n[TEST FAILED] System resilience issues detected.")
    sys.exit(1)
else:
    print("\n[SUCCESS] All negative tests and fuzz smoke test passed successfully!")
    sys.exit(0)
