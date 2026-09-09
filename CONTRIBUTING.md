# Contributing to the Corvus Programming Language 🐦

Thank you for your interest in contributing to **Corvus**! Whether you are fixing a bug, adding a new standard library module, optimizing TAC IR assembly code generation, or expanding documentation, your contributions are welcome.

---

## 🏗️ Architecture Overview

The Corvus compiler and runtime ecosystem follows a clean, modular design:

```
[Corvus Source (.crv)]
         │
         ▼
 1. Lexer (lexercorvus.py)       ────▶ Token Stream
         │
         ▼
 2. Parser (parsercorvus.py)     ────▶ Abstract Syntax Tree (AST)
         │
         ├───▶ 3a. Interpreter (evaluatorcorvus.py) ──▶ Execution Engine
         │
         ▼
 3b. TAC IR Generator            ────▶ Three-Address Code (TAC) IR
         │
         ▼
 4. v4.1 Super Optimizer         ────▶ Constant Folding, Strength Reduction, Peephole Pass
         │
         ▼
 5. Native Code Generator        ────▶ 64-bit NASM Assembly Binary (.exe / ELF)
```

---

## 📁 Repository Directory Structure

- **`Interpreter/`**: Core runtime interpreter, AST evaluator, REPL shell, and native module shims (`std_graphics.py`, `std_concurrency.py`, `std_net.py`, `std_json.py`, `std_memory.py`, `std_ffi.py`).
- **`Compiler_Core/`**: Intermediate Representation (IR), AST lowering, and the **v4.1 Super High-Level Optimizer Engine**.
- **`Compiler_Windows/`**, **`Compiler_Linux/`**, **`Compiler_MacOS/`**: Target assembly code generators emitting 64-bit NASM code.
- **`StdLib/`**: Standard library modules written natively in Corvus syntax (`math.crv`, `string.crv`, `graphics.crv`, `std_net.crv`, `std_json.crv`, `file.crv`, `sys.crv`).
- **`Examples-and-Tests/`**: Automated test suites and playable desktop game demos (Snake, Pong, Multi-Threaded Particle Engine).
- **`Editor-Extension/`**: VS Code extension package (`.vsix`) and Corvus Language Server Protocol (`corvus_lsp.py`).
- **`Documentation/webpage_corvus/` & `docs/`**: Official master documentation site hosted on GitHub Pages with embedded WebAssembly (Wasm) Playground.
- **`.github/workflows/ci.yml`**: GitHub Actions Matrix CI/CD building on Windows, Linux, and macOS.

---

## 🚀 How to Add a New Standard Library Module

1. **Implement Python Engine Shim (if native bindings needed)**:
   Add `std_yourmodule.py` in `Interpreter/` with clean static methods.
2. **Register Module in Evaluator**:
   Import `std_yourmodule.py` in `Interpreter/evaluatorcorvus.py` and register under `_setup_builtins()`.
3. **Create Corvus Module Header**:
   Create `StdLib/std_yourmodule.crv` exposing Corvus functions.
4. **Add Unit Tests**:
   Add test assertions in `Examples-and-Tests/matrix_regression_suite.py`.

---

## 🧪 Running Tests Before Submitting a PR

Before creating a Pull Request, verify that all linter checks and automated regression tests pass clean:

```bash
# 1. Run Syntax Linter Check
python Interpreter/Corvus.py --check Examples-and-Tests/01_hello_and_input.crv

# 2. Run Comprehensive Automated Matrix Test Suite
python Examples-and-Tests/matrix_regression_suite.py
```

---

## 📥 Submitting a Pull Request

1. **Fork the Repository** on GitHub.
2. **Create a Feature Branch**: `git checkout -b feature/my-new-feature`
3. **Commit your Changes**: `git commit -m "feat(stdlib): add crypto module"`
4. **Push to Branch**: `git push origin feature/my-new-feature`
5. **Open a Pull Request** against `main`!

Thank you for helping build the future of the **Corvus Programming Language**! 🐦
