<p align="center">
  <img src="Documentation/corvus_logo.png" alt="Corvus Programming Language Logo" width="240"/>
</p>

<h1 align="center">Corvus Programming Language</h1>

<p align="center">
  <b>A modern, multi-version systems and application language featuring explicit block scoping <code>[ ... ]</code>, static type annotations, first-class lambdas, OOP, Three-Address Code (TAC) IR Optimization, Self-Hosted Compiler, Deterministic Scope Memory Ref-Counting, and "Murder of Crows" 🐦 Concurrency Engine.</b>
</p>

<p align="center">
  <a href="#-repository-version-sitemap">Version Sitemap</a> •
  <a href="#-the-story-behind-corvus">The Story</a> •
  <a href="#-version-matrix--features">Version Matrix</a> •
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-license--author">License</a>
</p>

---

## 📂 Repository Version Sitemap

The Corvus codebase is structured into explicit, standalone version releases so users and developers can select, compare, or run any generation of the language:

| Directory | Version | Core Features | Execution Engine |
| :--- | :--- | :--- | :--- |
| **[`Version_1.1/`](Version_1.1/)** | **v1.1** | Basic AST Interpreter, Lambdas, OOP, CPM Package Manager | Python AST Visitor Interpreter |
| **[`Version_2.0/`](Version_2.0/)** | **v2.0** | Multi-Platform Native Assembly Compiler (`--target windows\|linux\|macos`), Pattern Matching, Pipeline Operator (`\|>`), Built-in Libs | NASM x86_64 Win64, ELF64, Mach-O Compiler & Interpreter |
| **[`Version_3.0/`](Version_3.0/)** | **v3.0** | **Self-Hosted Compiler (`CorvusCompiler.crv`)**, **Three-Address Code (TAC) IR Optimizer (Constant Folding & DCE)**, **Deterministic Scope Memory Ref-Counting**, **"Murder of Crows" 🐦 Concurrency Engine**, **Native C FFI (`ffi.load`, `ffi.bind`)**, **VS Code Extension v0.3.0** | Optimized TAC IR Compiler, Self-Hosted Corvus Compiler & Enterprise Interpreter |

---

## 📖 The Story Behind Corvus

> *"I got inspired to build my own programming language after watching a video about a programmer who created G# and C#, and a video by AstroSam. Since I already knew Python, I decided to take on the challenge and build my very own programming language from scratch!"*  
> — **Saatvik Jain** (Creator of Corvus)

**Corvus** was born out of curiosity and a passion for computer science. Instead of relying on indentation (like Python) or curly braces (like C/JavaScript), Corvus introduces a unique syntax using **square brackets `[ ... ]` for code blocks**, reserving **curly braces `{ ... }` for native lists**. 

It has grown from an interpreted prototype into a **self-hosted, IR-optimized systems language** with native cross-platform assembly generation (`CorvusC`) that outputs standalone binary executables!

---

## 🌟 Version Matrix & Features

### 1. Version 1.1 (`Version_1.1/`)
- Pure AST Visitor Interpreter.
- Lexically scoped environment trees, recursion, lambdas, classes, and Python bridge.

### 2. Version 2.0 (`Version_2.0/`)
- **Multi-Platform Assembly Generator**: Native 64-bit x86 NASM generation targeting Windows (Win64 ABI), Linux (ELF64 System V ABI), and macOS (Mach-O System V ABI).
- **Functional Pipeline (`|>`) & Pattern Matching (`match ... case ... else`)**.
- Built-in libraries (`math`, `system`, `gui`, `http`, `process`).

### 3. Version 3.0 (`Version_3.0/`)
- **⚡ Three-Address Code (TAC) Intermediate Representation (IR)**: Translates AST into linear TAC instructions (`ir.py`).
- **🔥 IR Optimization Passes (`optimizer.py`)**:
  - **Constant Folding**: Evaluates constant expressions like `2 + 3 -> 5` at compile time.
  - **Dead Code Elimination (DCE)**: Eliminates unreachable instructions and unused temporaries.
- **🐦 "Murder of Crows" Concurrency Engine (`crow`)**: Worker thread pools (`crow.fly`), thread synchronization (`crow.flock`), and thread-safe channels (`crow.channel`).
- **🧬 Native C Foreign Function Interface (`ffi`)**: Dynamic linking to native C shared libraries (`ffi.load`, `ffi.bind`, `ffi.call`) without Python dependencies.
- **💾 Deterministic Scope Memory Ref-Counting (`mem`)**: Automatic memory tracking and heap scope exit cleanup (`free`/`HeapFree`) in NASM assembly generation.
- **🚀 Self-Hosted Corvus Compiler & Interpreter**: `Compiler_SelfHosted/CorvusCompiler.crv` and `CorvusInterpreter.crv` written directly in pure Corvus syntax!
- **🎨 VS Code Extension v0.3.0**: Top-tier bracket pair colorization, auto-closing bracket rules, and snippets for `[...]`, `{...}`, `mem`, `ffi`, `crow`, and `mk func`.

---

## 🚀 Quickstart

### Prerequisites
* **Python 3.8+**
* Optional for Native Executable Compilation:
  ```powershell
  winget install NASM.NASM
  winget install MartinStorsjo.LLVM-MinGW.UCRT
  ```

---

### Executing Across Corvus Versions

#### Version 1.1 Interpreter
```bash
python Version_1.1/Interpreter/Corvus.py Version_1.1/Examples-and-Tests/02_recursion_factorial.crv
```

#### Version 2.0 Multi-Platform Compiler & Interpreter
```bash
# Interpreter
python Version_2.0/Interpreter/Corvus.py Version_2.0/Examples-and-Tests/09_pipeline_and_pattern_matching.crv

# Compiler
python Version_2.0/Compiler/CorvusC.py Version_2.0/Examples-and-Tests/09_pipeline_and_pattern_matching.crv --target windows -r
```

#### Version 3.0 Enterprise Engine (Self-Hosted, TAC IR & Concurrency)
```bash
# Corvus v3.0 Interpreter
python Version_3.0/Interpreter/Corvus.py Version_3.0/Examples-and-Tests/10_enterprise_memory_ffi_crows.crv

# Corvus v3.0 Self-Hosted Compiler Execution
python Version_3.0/Interpreter/Corvus.py Version_3.0/Compiler_SelfHosted/CorvusCompiler.crv

# Corvus v3.0 Native TAC IR Assembly Compiler
python Version_3.0/Compiler/CorvusC.py Version_3.0/Examples-and-Tests/10_enterprise_memory_ffi_crows.crv --target windows --keep-asm
```

---

## 📄 License & Author

Copyright (c) 2026 **Saatvik Jain**. All rights reserved.  
Distributed under the **MIT License**.
