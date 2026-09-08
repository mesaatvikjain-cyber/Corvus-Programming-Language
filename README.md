<p align="center">
  <img src="Documentation/corvus_logo.png" alt="Corvus Programming Language Logo" width="240"/>
</p>

<h1 align="center">Corvus Programming Language</h1>

<p align="center">
  <b>A modern, multi-version systems and application language featuring explicit block scoping <code>[ ... ]</code>, static type annotations, first-class lambdas, OOP, Three-Address Code (TAC) IR Optimization, Self-Hosted Compiler, Deterministic Scope Memory Ref-Counting, Interactive REPL, Native Standard Library Expansion, and VS Code Language Diagnostics.</b>
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
| **[`Version_3.0/`](Version_3.0/)** | **v3.0** | **Self-Hosted Compiler (`CorvusCompiler.crv`)**, **Three-Address Code (TAC) IR Optimizer**, **Ref-Counting GC**, **"Murder of Crows" 🐦 Concurrency Engine**, **Native C FFI** | Optimized TAC IR Compiler, Self-Hosted Corvus Compiler & Interpreter |
| **[`Version_3.1/`](Version_3.1/)** | **v3.1** | **Enterprise Error Handling & Resilience Engine**: **Call Stack Tracebacks**, **Panic-Mode Parser Recovery**, **Assembly Runtime Panic Guards (`__corvus_panic_null`, `__corvus_panic_bounds`)** | Resilient Multi-Platform TAC IR Compiler & Enterprise Interpreter |
| **[`Version_4.0/`](Version_4.0/)** | **v4.0** | **Native Corvus Standard Library Expansion (`math.crv`, `string.crv`, `file.crv`, `sys.crv`)**, **Advanced TAC IR Backend Optimizations (Function Inlining, Loop Unrolling, CSE)**, **Interactive REPL Shell (`repl.py`)**, **VS Code Extension v0.3.0 with Real-Time Language Diagnostics/Linter** | Full Enterprise TAC IR Compiler, Native Executable Compiler & Interactive REPL Shell |

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
- **🔥 IR Optimization Passes (`optimizer.py`)**: Constant Folding (`2 + 3 -> 5`) & Dead Code Elimination (DCE).
- **🐦 "Murder of Crows" Concurrency Engine (`crow`)**: Worker thread pools (`crow.fly`), thread synchronization (`crow.flock`), and thread-safe channels (`crow.channel`).
- **🧬 Native C Foreign Function Interface (`ffi`)**: Dynamic linking to native C shared libraries (`ffi.load`, `ffi.bind`, `ffi.call`).
- **💾 Deterministic Scope Memory Ref-Counting (`mem`)**: Automatic memory tracking and heap scope exit cleanup (`free`/`HeapFree`) in NASM assembly generation.
- **🚀 Self-Hosted Corvus Compiler & Interpreter**: `Compiler_SelfHosted/CorvusCompiler.crv` and `CorvusInterpreter.crv` written directly in pure Corvus syntax!

### 4. Version 3.1 (`Version_3.1/`)
- **🛡️ Enterprise Error Handling & Resilience Engine**:
  - **Visual Diagnostics & Call Stack Tracebacks**: Formatted error reports displaying active function call stack frames and caret pointers (`^^^^^`).
  - **Panic-Mode Parser Recovery (`synchronize()`)**: Prevents cascading compilation failure by skipping to the next statement boundary upon syntax errors.
  - **Assembly Runtime Safety Guards**: Native assembly guards (`__corvus_panic_null`, `__corvus_panic_bounds`, `__corvus_panic_divzero`).

### 5. Version 4.0 (`Version_4.0/`)
- **📚 Native Corvus Standard Library Expansion (`StdLib/`)**:
  - `math.crv`: `abs`, `max`, `min`, `pow`, `factorial`, `clamp`, `sqrt_approx`.
  - `string.crv`: `repeat_str`, `pad_left`, `pad_right`, `is_empty`.
  - `file.crv`: `read_all`, `write_all`, `file_exists`.
  - `sys.crv`: `get_platform`, `get_version`.
- **🚀 Advanced TAC IR Compiler Optimizations (`Compiler_Core/optimizer.py`)**:
  - **Function Inlining Pass (`inlining_pass`)**: Inlines non-recursive leaf functions to eliminate call overhead.
  - **Loop Unrolling Pass (`loop_unrolling_pass`)**: Detects and expands small fixed-iteration loops in TAC IR.
  - **Common Subexpression Elimination (`cse_pass`)**: Eliminates redundant expression computations across basic blocks.
- **💻 Interactive REPL Shell (`Interpreter/repl.py`)**:
  - Multi-line block detection (unclosed braces/parentheses).
  - Tab auto-completion for keywords, builtins, and active symbols.
  - Interactive state directives (`.help`, `.vars`, `.funcs`, `.clear`, `.reset`, `.exit`).
- **🔌 VS Code Extension Enhancements v0.3.0 (`Editor-Extension/`)**:
  - Real-time Language Diagnostics / Syntax Linter on save.
  - Inline execution commands (`Corvus: Run File in Interpreter`, `Corvus: Compile & Run Native Binary`).
  - Integrated status bar execution control (`▶ Run Corvus`).

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

#### Launching the Interactive REPL Shell (v4.0)
```bash
python Version_4.0/Interpreter/Corvus.py --repl
```

#### Running Version 4.0 Test Suite
```bash
# Interpreter
python Version_4.0/Interpreter/Corvus.py Version_4.0/Examples-and-Tests/12_version4_suite.crv

# Native Windows Executable Compiler
python Version_4.0/Compiler_Windows/CorvusC_win64.py Version_4.0/Examples-and-Tests/12_version4_suite.crv
```

---

## 📜 License & Author

- **Author**: Saatvik Jain
- **License**: MIT License
