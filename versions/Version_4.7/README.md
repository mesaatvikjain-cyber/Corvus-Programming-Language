# Corvus Programming Language — Version 4.7

**Corvus v4.7** is the Enterprise Security Hardening, Robustness & Fuzz-Tested release of the Corvus programming language.

## 🌟 Key Highlights in Version 4.7

1. **RavenAI Built-in Developer Assistant (`corvus ai`)**:
   - **Interactive Terminal Chat (`corvus ai`)**: Live conversational session with Corvus's specialized AI assistant.
   - **Typo-Tolerant & Fuzzy Semantic Q&A (`corvus ai ask`)**: Understands questions about Corvus syntax even with severe typos (*funtion*, *matix*, *concurancy*) via SequenceMatcher.
   - **Structural Code Explainer (`corvus ai explain`)**: Analyzes any Corvus file or snippet, reporting imported modules, classes, functions, loops, and matrix operations.
   - **Diagnostic Bug Fixer (`corvus ai fix`)**: Detects Pythonisms (`print` -> `log`, `def` -> `mk func`, `return` -> `givout`), catches syntax errors, and synthesizes instant patches.
   - **Python-to-Corvus Transpiler (`corvus ai translate`)**: Automatically converts Python scripts into idiomatic Corvus code with block-aware bracket indentation mapping.
   - **100% Offline & Zero External Dependencies**: Runs out of the box with pure Python standard library.

2. **Enterprise Security Hardening**:
   - **Zero shell=True subprocess execution**: All system commands run via sanitized argument arrays.
   - **SSRF Protection & URL Scheme Whitelisting**: Network operations reject unsafe schemas (file://, ftp://) and restrict requests to http:// and https://.
   - **Resource Bounds Enforcement**: Hard limit of 10MB payload sizes on file reads, network downloads, and allocations to prevent DoS attacks.
   - **SQL Injection Prevention**: Safe parameterization in SQLite operations via db.query_params().
   - **Cryptographic Security**: First-class support for HMAC-SHA256, SHA-512, and cryptographically secure random bytes via crypto.secure_random_bytes().
   - **Call Stack & Deserializer Protection**: Maximum recursion stack depth bounds (MAX_STACK_DEPTH = 10000) and safe bounds-checked bytecode deserialization.

3. **Categorized Negative Test Suite (test/)**:
   - **28 targeted negative test cases** spanning variables, conditions, loops, functions, oop, expressions.
   - **Automated Grammar-Aware Fuzzing Engine (test/fuzzer.py)** enforcing zero unhandled crashes.

---

## 🤖 Using RavenAI CLI

```bash
# 1. Launch interactive RavenAI assistant chat
corvus ai

# 2. Ask any question about Corvus syntax or features (with typo tolerance!)
corvus ai ask "How do classes and constructors work in Corvus?"

# 3. Analyze and explain any Corvus file or snippet
corvus ai explain Examples-and-Tests/17_matrix_matmul_suite.crv

# 4. Diagnose broken scripts and synthesize automatic patches
corvus ai fix broken_script.crv

# 5. Transpile Python source code directly into valid Corvus code
corvus ai translate script.py
```

---

## 🚀 Running Tests & Fuzzer

```bash
# 1. Run all categorized negative tests
python test/run_all_tests.py

# 2. Run automated fuzzer with 100 iterations (10 second timeout per test)
python test/fuzzer.py -n 100 -t 10

# 3. Run all standard functional test suites
python Interpreter/Corvus.py test Examples-and-Tests
```

---

## 💻 Quickstart

```bash
# Run a Corvus script via AST Interpreter
python Interpreter/Corvus.py Examples-and-Tests/22_security_hardening_suite.crv

# Run with Bytecode VM
python Interpreter/Corvus.py --vm Examples-and-Tests/21_bytecode_vm_suite.crv

# Compile to standalone binary executable via C99 backend (-O3)
python Compiler/CorvusC_c.py Examples-and-Tests/01_comprehensive_suite.crv -o app.exe -O3 --run
```
