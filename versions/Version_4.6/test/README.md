# 🧪 Corvus Negative & Stress Test Suite (`test/`)

Welcome to the **Corvus Negative & Stress Testing Framework**. This directory contains deliberately malformed, structurally invalid, and buggy Corvus scripts categorized by feature area, along with an automated **Mutational & Grammar Fuzzing Engine**.

---

## 📁 Directory Layout

```text
test/
├── run_all_tests.py     # Master runner testing all categories + fuzzer smoke test
├── fuzzer.py            # Mutational & grammar-based random code generator & stress tester
├── variables/           # Type mismatches, unassigned consts, missing identifiers
├── conditions/          # Dangling else, unclosed brackets, bad ternaries
├── loops/               # Misplaced break/continue, invalid for-in targets
├── functions/           # Arity mismatches, bad lambdas, duplicate arguments
├── oop/                 # Missing class bodies, invalid 'this' scope, bad init
├── expressions/         # Invalid operator stacking, unclosed strings & f-strings
└── fuzz_corpus/         # Seed snippets and automated crash dumps
```

---

## 🚀 Running the Tests

### 1. Run All Categorized Negative Tests & Fuzz Smoke Test
```bash
python test/run_all_tests.py
```
This verifies that **every** malformed input is caught gracefully by `CorvusError` and that no unhandled Python exceptions (e.g., `IndexError`, `KeyError`, `AttributeError`) occur.

### 2. Run the Fuzzer
Run 200 iterations of randomized mutational stress-testing:
```bash
python test/fuzzer.py --iterations 200 --timeout 30
```

Any unexpected crash will automatically be captured and saved in `test/fuzz_corpus/crashes/` for reproducible debugging.
