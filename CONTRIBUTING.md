# Contributing to the Corvus Programming Language 🐦

Thank you for your interest in contributing to **Corvus**! Whether you are fixing a bug, adding a new standard library module, optimizing TAC IR assembly code generation, or expanding documentation, your contributions are welcome.

---

## 🏗️ Architecture Overview

The Corvus compiler and runtime ecosystem follows a modern Tri-Engine design:

```
                      [Corvus Source (.crv)]
                                │
                                ▼
                       1. Tokenizer & Lexer (lexercorvus.py)
                                │
                                ▼
                       2. Parser (parsercorvus.py) ──▶ Abstract Syntax Tree (AST)
                                │
       ┌────────────────────────┼────────────────────────┐
       ▼                        ▼                        ▼
 [AST Interpreter]       [Bytecode VM]            [C99 Transpiler]
  evaluatorcorvus.py      compiler_vm.py           CorvusC_c.py
       │                  bytecode.py              Compiler_Core/
       │                  vm.py (.crvc)                  │
       ▼                        │                        ▼
  RavenAI Assistant             ▼                  Native Executable
   (ai_engine.py)          CorvusVM Exec                (-O3)
```

---

## 📁 Repository Directory Structure

- **`Interpreter/`**: Core runtime interpreter, AST evaluator, REPL shell, Bytecode Virtual Machine, native module shims, and **`ai_engine.py` (RavenAI Intelligent Assistant)**.
- **`Compiler/`**: High-performance C99 native compilation pipeline driver (`CorvusC_c.py`).
- **`Compiler_Core/`**: Intermediate Representation (IR), AST lowering, and C99 code generator.
- **`Compiler_Windows/`**, **`Compiler_Linux/`**, **`Compiler_MacOS/`**: Target assembly code generators emitting 64-bit NASM code.
- **`StdLib/`**: 30+ standard library modules written natively in Corvus syntax (`math.crv`, `string.crv`, `graphics.crv`, `sqlite.crv`, `torch.crv`, `numpy.crv`).
- **`test/`**: **Categorized Negative Test Suite** (`variables/`, `conditions/`, `loops/`, `functions/`, `oop/`, `expressions/`) and automated grammar-aware **`fuzzer.py`**.
- **`Examples-and-Tests/`**: Automated functional test suites and playable desktop game demos (Snake, Pong).
- **`Distributions/`**: Zero-dependency standalone binary releases and portable SDK bundles (`Version_5.0/`, `Version_4.7/`, `Version_4.6/`, `Version_4.5/`, `Version_4.4/`).
- **`versions/`**: Historical release snapshots from `Version_1.1` to `Version_5.0`.
- **`Documentation/`**: Master Documentation, tutorials (`01_...` through `13_v5.0_...`), Installation Guide, and Hosting documentation.
- **`Editor-Extension/`**: VS Code extension package (`.vsix`) and Language Server Protocol daemon (`corvus lsp`).

---

## 🚀 How to Add a New Standard Library Module

1. **Implement Python Engine Shim (if native bindings needed)**:
   Add `std_yourmodule.py` in `Interpreter/` with clean static methods.
2. **Register Module in Evaluator**:
   Import `std_yourmodule.py` in `Interpreter/evaluatorcorvus.py` and register under `_setup_builtins()`.
3. **Create Corvus Module Header**:
   Create `StdLib/std_yourmodule.crv` exposing canonical Corvus functions.
4. **Add Unit Tests**:
   Add test assertions in `Examples-and-Tests/` and run the test runner.

---

## 🧪 Running Tests Before Submitting a PR

Before creating a Pull Request, verify that all negative tests, fuzzing, and functional regression test suites pass 100%:

```bash
# 1. Run all 28 Categorized Negative Tests
python test/run_all_tests.py

# 2. Run Automated Fuzzing Engine Stress Test
python test/fuzzer.py -n 100 -t 10

# 3. Run Standard Functional Test Suites
python Interpreter/Corvus.py test Examples-and-Tests

# 4. Use RavenAI to analyze and validate your new files
python Interpreter/Corvus.py ai explain path/to/your_file.crv
```

---

## 📥 Submitting a Pull Request

1. **Fork the Repository** on GitHub.
2. **Create a Feature Branch**: `git checkout -b feature/my-new-feature`
3. **Commit your Changes**: `git commit -m "feat(stdlib): add crypto module"`
4. **Push to Branch**: `git push origin feature/my-new-feature`
5. **Open a Pull Request** against `main`!

Thank you for helping build the future of the **Corvus Programming Language**! 🐦
