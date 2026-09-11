# Corvus Programming Language — Version 4.6

**Corvus v4.6** is the Enterprise Security Hardening, Robustness & Fuzz-Tested release of the Corvus programming language.

## 🌟 Key Highlights in Version 4.6

1. **Enterprise Security Hardening**:
   - **Zero shell=True subprocess execution**: All system commands run via sanitized argument arrays.
   - **SSRF Protection & URL Scheme Whitelisting**: Network operations reject unsafe schemas (file://, ftp://) and restrict requests to http:// and https://.
   - **Resource Bounds Enforcement**: Hard limit of 10MB payload sizes on file reads, network downloads, and allocations to prevent DoS attacks.
   - **SQL Injection Prevention**: Safe parameterization in SQLite operations via db.query_params().
   - **Cryptographic Security**: First-class support for HMAC-SHA256, SHA-512, and cryptographically secure random bytes via crypto.secure_random_bytes().
   - **Call Stack & Deserializer Protection**: Maximum recursion stack depth bounds (MAX_STACK_DEPTH = 10000) and safe bounds-checked bytecode deserialization.

2. **Categorized Negative Test Suite (test/)**:
   - **28 targeted negative test cases** spanning:
     - variables/: invalid redeclarations, missing initializers, invalid identifiers, type mismatches.
     - conditions/: malformed ternaries, missing branches, invalid logical expressions.
     - loops/: unclosed blocks, invalid step ranges, break/continue outside loops.
     - functions/: duplicate parameter names, missing bodies, arity mismatches.
     - oop/: circular inheritance, missing class bodies, invalid super calls.
     - expressions/: operator misuse, unbalanced brackets/parentheses, bad lambda syntax.

3. **Automated Grammar-Aware Fuzzing Engine (test/fuzzer.py)**:
   - Stress-tests Lexer, Parser, AST Evaluator, and Bytecode Compiler with randomized token mutations, structural chaos, and malformed inputs.
   - Enforces **zero unhandled exceptions** — all invalid code must produce clean CorvusError diagnostics.

---

## 🚀 Running Tests & Fuzzer

\\ash
# 1. Run all categorized negative tests
python test/run_all_tests.py

# 2. Run automated fuzzer with 100 iterations (10 second timeout per test)
python test/fuzzer.py -n 100 -t 10

# 3. Run all standard functional test suites
python Interpreter/Corvus.py test Examples-and-Tests
\
---

## 💻 Quickstart

\\ash
# Run a Corvus script via AST Interpreter
python Interpreter/Corvus.py Examples-and-Tests/22_security_hardening_suite.crv

# Run with Bytecode VM
python Interpreter/Corvus.py --vm Examples-and-Tests/21_bytecode_vm_suite.crv

# Compile to standalone binary executable via C99 backend (-O3)
python Compiler/CorvusC_c.py Examples-and-Tests/01_comprehensive_suite.crv -o app.exe -O3 --run
\
