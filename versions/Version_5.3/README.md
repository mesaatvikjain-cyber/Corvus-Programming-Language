<p align="center">
  <img src="Documentation/corvus_logo.png" alt="Corvus Programming Language Logo" width="240"/>
</p>

<h1 align="center">Corvus Programming Language</h1>

<p align="center">
  <b>A modern, multi-version systems and application language featuring explicit block scoping <code>[ ... ]</code>, static type annotations, first-class lambdas, OOP, Three-Address Code (TAC) IR Optimization, Self-Hosted Compiler, Deterministic Scope Memory Ref-Counting, Interactive REPL, Super High-Level Optimization Engine, and VS Code Language Diagnostics.</b>
</p>

<p align="center">
  <a href="Documentation/PROJECT_STRUCTURE.md"><b>🧭 Project Structure</b></a> •
  <a href="Documentation/webpage_corvus/index.html"><b>🌐 Documentation Webpage</b></a> •
  <a href="Documentation/INSTALLATION_GUIDE.md"><b>🛠️ Automated Installers Guide</b></a> •
  <a href="#-hands-on-version-tutorials"><b>📚 Version Tutorials</b></a> •
  <a href="Documentation/HOSTING.md"><b>☁️ Hosting Guide</b></a> •
  <a href="#-repository-version-sitemap">Version Sitemap</a> •
  <a href="#-the-story-behind-corvus">The Story</a>
</p>

---

## 📦 Zero-Dependency Standalone Distributions & Portable SDK (v5.3 - v4.4)

Corvus ships with **100% zero-dependency, standalone native executables** and a **portable SDK bundle** inside [`Distributions/Version_5.3/`](Distributions/Version_5.3/README.md), [`Distributions/Version_5.1/`](Distributions/Version_5.1/README.md), [`Distributions/Version_5.0/`](Distributions/Version_5.0/README.md), [`Distributions/Version_4.7/`](Distributions/Version_4.7/README.md), [`Distributions/Version_4.6/`](Distributions/Version_4.6/README.md), [`Distributions/Version_4.5/`](Distributions/Version_4.5/README.md) and [`Distributions/Version_4.4/`](Distributions/Version_4.4/README.md). **No Python installation is required!**

* **🌟 Tier 1: Standalone Single-File Executables (`standalone/`)**:
  - `corvus.exe` — Self-contained Corvus v5.3 cognitive engine with **RavenLM Neural Transformer Language Model (166k weights)**, Autoregressive Code Completion (`corvus ai complete`), Neural Code Gen (`corvus ai gen`), Model Inspection (`corvus ai model`), Fine-Tuning Pipeline (`corvus ai train`), Tiered JIT Compiler Engine, Async WebSockets & Channels, GameKit 2D Physics & Retro Audio, SQLite ORM & DataFrames, CPM 2.0 Package Manager, Interactive CLI Tour, Language Server Protocol (LSP) Daemon, WebAssembly (Wasm) Backend, Micro Web Server, Bytecode VM, `.crvc` Binary Compiler, Disassembler, Interpreter, REPL, Linter, Formatter, and Profiler.
  - `corvusc.exe` — Self-contained C99 Native Compiler driver with `-O3` pipeline optimization.
  - One-click installer: Run `.\Distributions\Version_5.2\install_standalone_windows.ps1` (or `bash install_standalone_linux.sh` / `bash install_standalone_macos.sh`).
* **🧰 Tier 2: All-in-One Portable SDK (`portable-sdk/`)**:
  - Includes `bin/corvus.bat`, `bin/corvusc.bat`, pre-trained neural weights (`raven_weights.pt`, `raven_weights.json`), standard library (`StdLib/`), examples, and zero-config embedded runtime bootstrap.

---

## 🛠️ Automated Cross-Platform Installers (v1.1 - v5.3)

Corvus includes self-contained automated installer scripts for **Windows** (PowerShell), **Linux** (Bash), and **macOS** (Zsh/Bash) for **every single version release**!

### Quick One-Line Install Command
* **Windows (PowerShell Master Installer — includes Option [0] Standalone Native Binaries)**:
  ```powershell
  .\install_windows.ps1
  ```
* **Linux (Master Installer — includes Option [0] Standalone Binaries)**:
  ```bash
  bash install_linux.sh
  ```
* **macOS (Master Installer — includes Option [0] Standalone Binaries)**:
  ```bash
  bash install_macos.sh
  ```

For detailed version-by-version installation steps, see [Documentation/INSTALLATION_GUIDE.md](Documentation/INSTALLATION_GUIDE.md) and [Distributions/Version_5.3/README.md](Distributions/Version_5.3/README.md).

---

## 🌐 Official Documentation Website (`webpage_corvus`)

Corvus features a complete, interactive, self-contained **Master Documentation Website** located inside [`Documentation/webpage_corvus/`](Documentation/webpage_corvus/index.html) (and mirrored in [`docs/`](docs/index.html) for GitHub Pages).

### 🚀 Highlights of the Documentation Webpage
- **Interactive Version Tutorials (v1.1 - v5.3)**: Hands-on code walkthroughs with interactive tab selectors.
- **Language Syntax Quick Cheat Sheet**: Rapid reference cards for variables, control flow, functions, and OOP.
- **19 Exhaustive Chapters**: Covers Language Story, Syntax, Control Flow, Lambdas, OOP, Functional Pipelines, Ref-Counting Memory GC, "Murder of Crows" Concurrency, Native C FFI, 30+ Standard Libraries, TAC IR Compiler, v4.1 Super Optimizer, Desktop 2D Graphics, AI/ML Suite, Rust-Style Diagnostics, VS Code Tooling, v5.0 Enterprise Ecosystem, v5.1 Omni-Platform & Real-Time Ecosystem, and v5.2 Deep Learning Neural AI & Cognitive Ecosystem.
- **In-Browser Wasm Playground & IDE**: Interactive sandbox powered by Pyodide and WebAssembly.
- **Free Online Hosting Support**: Easily host on **GitHub Pages**, **Vercel**, **Netlify**, or **Cloudflare Pages**. See [Documentation/HOSTING.md](Documentation/HOSTING.md) for step-by-step instructions.

---

## 📚 Hands-on Version Tutorials (`Documentation/tutorials/`)

Every version release of Corvus includes a dedicated Markdown hands-on tutorial guide:

* **[Version 1.1 Tutorial](Documentation/tutorials/01_v1.1_basics_and_interpreter_tutorial.md)**: AST Interpreter, Scope Trees, Lambdas, OOP Classes, CPM Packages.
* **[Version 2.0 Tutorial](Documentation/tutorials/02_v2.0_multiplatform_compiler_tutorial.md)**: Multi-Platform Native NASM Compilation (Windows Win64, Linux ELF64, macOS Mach-O), Pipeline `|>`, Pattern Matching.
* **[Version 3.0 Tutorial](Documentation/tutorials/03_v3.0_selfhosted_concurrency_ffi_tutorial.md)**: "Murder of Crows" 🐦 Concurrency Engine, Native C FFI, Memory Ref-Counting GC, Self-Hosted Compiler.
* **[Version 3.1 Tutorial](Documentation/tutorials/04_v3.1_error_handling_resilience_tutorial.md)**: Visual Stack Tracebacks, Panic-Mode Parser Recovery (`synchronize()`), Assembly Safety Guards.
* **[Version 4.0 Tutorial](Documentation/tutorials/05_v4.0_stdlib_repl_vscode_tutorial.md)**: Native Standard Library (`math.crv`, `string.crv`, `file.crv`, `sys.crv`), Interactive REPL Shell Directives, VS Code Extension v0.3.0.
* **[Version 4.1 Tutorial](Documentation/tutorials/06_v4.1_super_optimization_engine_tutorial.md)**: Super High-Level IR Optimization Engine (Constant Propagation, Strength Reduction `x * 4 -> SHL`, Branch Folding, Peephole Assembly Pass).
* **[Version 4.2 Tutorial](Documentation/tutorials/07_v4.2_desktop_graphics_and_concurrency_tutorial.md)**: Zero-Config Desktop 2D Graphics Canvas (`graphics.crv`), Keyboard/Mouse Event Loop, and Expanded "Murder of Crows" Concurrency.
* **[Version 4.3 Tutorial](Documentation/tutorials/08_v4.3_ai_ml_suite_and_diagnostics_tutorial.md)**: AI & Deep Learning Stack (`tensorflow`, `torch`, `numpy`, `pandas`, `scikit_learn`, `transformers`), 30+ Standard Library Modules, and Rust-Style Diagnostic Knowledge Base (`--explain`, `--ai-fix`).
* **[Version 4.4 Tutorial](Documentation/tutorials/09_v4.4_syntax_ergonomics_and_type_inference_tutorial.md)**: Modern Syntax Ergonomics, Universal Dual Brackets (`{ ... }` / `[ ... ]`), Smart Type Inference (`set x = 10`), Top-level `const`, Semicolon-optional typed declarations.
* **[Version 4.5 Tutorial](Documentation/tutorials/10_v4.5_bytecode_vm_and_compiler_tutorial.md)**: Corvus Bytecode Virtual Machine (`CorvusVM`), Compact `.crvc` Binary Executable Specification, Bytecode Compiler & Disassembler (`corvus compile`, `corvus dis`, `corvus --vm`).
* **[Version 4.6 Tutorial](Documentation/tutorials/11_v4.6_security_hardening_and_resilience_tutorial.md)**: Enterprise Security Hardening, Subprocess Sanitization, SSRF/DoS Bounds Guards, SQLite Prepared Sequences, Hardened Bytecode Deserializer, and VM Stack Guards.
* **[Version 4.7 Tutorial](Documentation/tutorials/12_v4.7_raven_ai_assistant_and_transpiler_tutorial.md)**: Built-in RavenAI Developer Assistant, Typo-Tolerant Knowledge Base, Code Explainer, Diagnostic Auto-Fixer, and Python-to-Corvus Transpiler.
* **[Version 5.0 Tutorial](Documentation/tutorials/13_v5.0_enterprise_ecosystem_tutorial.md)**: Enterprise Ecosystem: RavenAI 2.0 (Automated TestGen, DocGen, Code Review, Reverse Transpiler), CPM 2.0 Package Manager, Native Micro Web Framework, Interactive Terminal Tour, Language Server Protocol (LSP), and WebAssembly (Wasm) Export.
* **[Version 5.1 Tutorial](Documentation/tutorials/14_v5.1_omni_platform_and_realtime_ecosystem_tutorial.md)**: Omni-Platform & Real-Time Ecosystem: Tiered JIT Bytecode Compiler Engine (`--jit`), Real-Time Async WebSockets & Channels (`web.ws_server`, `channel`), In-Browser Wasm Playground, RavenAI 3.0 Code Gen & Auto-Refactoring, 2D GameKit & Retro Audio Synthesizer, and Active-Record SQLite ORM & Reactive DataFrames.
* **[Version 5.2 Tutorial](Documentation/tutorials/15_v5.2_real_neural_ai_model_tutorial.md)**: Deep Learning Neural AI & Cognitive Ecosystem: RavenLM In-Tree Neural Transformer Language Model (166k weights), Autoregressive Code Completion (`corvus ai complete`), Model Specs (`corvus ai model`), Fine-Tuning Pipeline (`corvus ai train`), and Zero-Dependency Dual Inference (PyTorch & pure NumPy fallback).

---

## 📂 Repository Version Sitemap

The Corvus codebase is structured into explicit, standalone version releases so users and developers can select, compare, or run any generation of the language:

| Directory | Version | Core Features | Execution Engine | Installer Scripts |
| :--- | :--- | :--- | :--- | :--- |
| **[`versions/Version_5.2/`](versions/Version_5.2/)** | **v5.2** | **Deep Learning Neural AI & Cognitive Ecosystem**: **RavenLM Neural Transformer (166k weights)**, **Autoregressive Code Completion (`corvus ai complete`)**, **Neural Code Gen (`corvus ai gen`)**, **Model Inspector (`corvus ai model`)**, **Fine-Tuning Pipeline (`corvus ai train`)**, **Dual-Runtime PyTorch & NumPy Engine** | Cognitive Neural Engine: In-Memory Causal Transformer, Tiered JIT Compiler, Bytecode VM, and C99 Native Transpiler | [`Win`](versions/Version_5.2/install_windows.ps1) \| [`Linux`](versions/Version_5.2/install_linux.sh) \| [`macOS`](versions/Version_5.2/install_macos.sh) |
| **[`versions/Version_5.1/`](versions/Version_5.1/)** | **v5.1** | **Omni-Platform & Real-Time Ecosystem**: **Tiered JIT Compiler (`corvus --jit`)**, **Async Channels (`channel.new()`) & WebSockets (`web.ws_server()`)**, **In-Browser Wasm Playground & IDE**, **RavenAI 3.0 (`corvus ai gen`, `corvus ai refactor`)**, **Corvus GameKit (`gamekit`) & Retro Audio (`audio`) with 3 Playable Games**, **Active-Record SQLite ORM (`orm`) & Reactive DataFrames (`dataframe`)** | Omni-Platform Quad-Engine: Dynamic JIT Compiler, Stack Bytecode VM, C99 Native Transpiler, and Multi-Platform Interpreter | [`Win`](versions/Version_5.1/install_windows.ps1) \| [`Linux`](versions/Version_5.1/install_linux.sh) \| [`macOS`](versions/Version_5.1/install_macos.sh) |
| **[`versions/Version_5.0/`](versions/Version_5.0/)** | **v5.0** | **Enterprise Developer Ecosystem**: **RavenAI 2.0 (`testgen`, `doc`, `review`, `export`)**, **CPM 2.0 Package Manager (`corvus.json` / `corvus.lock`)**, **Native Micro Web Framework (`web.server()`)**, **Interactive Terminal Tour (`corvus tour`)**, **Language Server Protocol Daemon (`corvus lsp`)**, **WebAssembly Backend (`corvus compile --target wasm`)** | Enterprise Polyglot Engine: AI-Powered Interpreter, Stack Bytecode VM, C99 Native Compiler, LSP Server & Wasm Emitter | [`Win`](versions/Version_5.0/install_windows.ps1) \| [`Linux`](versions/Version_5.0/install_linux.sh) \| [`macOS`](versions/Version_5.0/install_macos.sh) |
| **[`versions/Version_4.7/`](versions/Version_4.7/)** | **v4.7** | **"RavenAI" Built-in AI Assistant & Transpiler**: **Interactive AI Chat Assistant (`corvus ai`)**, **Typo-Tolerant & Fuzzy Semantic Q&A (`corvus ai ask`)**, **Structural Code Explainer & AST Inspector (`corvus ai explain`)**, **Diagnostic Bug Analysis & Automatic Patch Synthesis (`corvus ai fix`)**, **Python-to-Corvus Code Transpiler (`corvus ai translate`)** | AI-Augmented Tri-Engine Architecture: Intelligent AST Interpreter, Bytecode VM, and C99 Native Compiler | [`Win`](versions/Version_4.7/install_windows.ps1) \| [`Linux`](versions/Version_4.7/install_linux.sh) \| [`macOS`](versions/Version_4.7/install_macos.sh) |
| **[`versions/Version_1.1/`](versions/Version_1.1/)** | **v1.1** | Basic AST Interpreter, Lambdas, OOP, CPM Package Manager | Python AST Visitor Interpreter | [`Win`](versions/Version_1.1/install_windows.ps1) \| [`Linux`](versions/Version_1.1/install_linux.sh) \| [`macOS`](versions/Version_1.1/install_macos.sh) |
| **[`versions/Version_2.0/`](versions/Version_2.0/)** | **v2.0** | Multi-Platform Native Assembly Compiler (`--target windows\|linux\|macos`), Pattern Matching, Pipeline Operator (`\|>`), Built-in Libs | NASM x86_64 Win64, ELF64, Mach-O Compiler & Interpreter | [`Win`](versions/Version_2.0/install_windows.ps1) \| [`Linux`](versions/Version_2.0/install_linux.sh) \| [`macOS`](versions/Version_2.0/install_macos.sh) |
| **[`versions/Version_3.0/`](versions/Version_3.0/)** | **v3.0** | **Self-Hosted Compiler (`CorvusCompiler.crv`)**, **Three-Address Code (TAC) IR Optimizer**, **Ref-Counting GC**, **"Murder of Crows" 🐦 Concurrency Engine**, **Native C FFI** | Optimized TAC IR Compiler, Self-Hosted Corvus Compiler & Interpreter | [`Win`](versions/Version_3.0/install_windows.ps1) \| [`Linux`](versions/Version_3.0/install_linux.sh) \| [`macOS`](versions/Version_3.0/install_macos.sh) |
| **[`versions/Version_3.1/`](versions/Version_3.1/)** | **v3.1** | **Enterprise Error Handling & Resilience Engine**: **Call Stack Tracebacks**, **Panic-Mode Parser Recovery**, **Assembly Runtime Panic Guards (`__corvus_panic_null`, `__corvus_panic_bounds`)** | Resilient Multi-Platform TAC IR Compiler & Enterprise Interpreter | [`Win`](versions/Version_3.1/install_windows.ps1) \| [`Linux`](versions/Version_3.1/install_linux.sh) \| [`macOS`](versions/Version_3.1/install_macos.sh) |
| **[`versions/Version_4.0/`](versions/Version_4.0/)** | **v4.0** | **Native Corvus Standard Library Expansion (`math.crv`, `string.crv`, `file.crv`, `sys.crv`)**, **Advanced TAC IR Backend Optimizations**, **Interactive REPL Shell (`repl.py`)**, **VS Code Extension v0.3.0** | Full Enterprise TAC IR Compiler, Native Executable Compiler & Interactive REPL | [`Win`](versions/Version_4.0/install_windows.ps1) \| [`Linux`](versions/Version_4.0/install_linux.sh) \| [`macOS`](versions/Version_4.0/install_macos.sh) |
| **[`versions/Version_4.1/`](versions/Version_4.1/)** | **v4.1** | **Super High-Level Optimization Engine**: **Constant Propagation**, **Algebraic Strength Reduction (`x * 2^n -> x << n`, `x / 2^n -> x >> n`)**, **Constant Branch Folding (`if (1)`)**, **CFG Jump Threading**, **Assembly Peephole Optimization** | Super-Optimized TAC IR Compiler & Native Executable Generator | [`Win`](versions/Version_4.1/install_windows.ps1) \| [`Linux`](versions/Version_4.1/install_linux.sh) \| [`macOS`](versions/Version_4.1/install_macos.sh) |
| **[`versions/Version_4.2/`](versions/Version_4.2/)** | **v4.2** | **Desktop 2D Graphics Canvas (`graphics.crv`)**, Zero-Config Window/Shape/Event Rendering Loop (`graphics.fps(60)`), Playable Snake/Pong Games, Expanded "Murder of Crows" Concurrency (`crow.parallel_map`, `crow.race`, `crow.nest`) | Real-time Desktop Canvas Engine, Parallel Crows Concurrency, Super-Optimized Compiler | [`Win`](versions/Version_4.2/install_windows.ps1) \| [`Linux`](versions/Version_4.2/install_linux.sh) \| [`macOS`](versions/Version_4.2/install_macos.sh) |
| **[`versions/Version_4.3/`](versions/Version_4.3/)** | **v4.3** | **100% Compiler-Interpreter Parity & Modern Tooling**: **Native Matrix Multiplication Operator (`@`)**, **C99 Transpiler Backend (`-O3`)**, **AST Constant Folding & Pruning Optimizer**, **High-Precision Benchmarking & AST Profiler**, **Modern F-Strings (`f"..."`) & Inline Ternaries (`? :`)**, **Dynamic Dictionaries in Native Code**, **Strict Static Type Checker (`--strict`)**, **Canonical Formatter (`fmt`)**, **Test Runner (`test`)**, **Integrated CPM Package Manager**, **Rust-Style Diagnostic Catalog (`--explain <CODE>`)**, **Levenshtein Typo Heuristics** | Complete Dual Engine: Enterprise AI/ML Interpreter & Ultra-Fast Native C99/Assembly Compiler with 100% Feature Parity | [`Win`](versions/Version_4.3/install_windows.ps1) \| [`Linux`](versions/Version_4.3/install_linux.sh) \| [`macOS`](versions/Version_4.3/install_macos.sh) |
| **[`versions/Version_4.4/`](versions/Version_4.4/)** | **v4.4** | **Modern Syntax Ergonomics & Universal Dual Brackets**: **Smart Type Inference (`set x = 10`)**, **Universal Dual Brackets for Code Blocks (`{ ... }` and `[ ... ]`)**, **Universal Dual Brackets for Lists (`[ ... ]` and `{ ... }`)**, **First-Class Top-Level `const` Declarations**, **Semicolon-Optional Typed Declarations (`set int count = 42`)**, **Flexible Expression Conditionals without mandatory parentheses**, **100% Dual Engine Parity across Interpreter & C99 Native Compiler** | Full Modern Ergonomics Interpreter & Ultra-Fast Native C99 Compiler (-O3) with Zero Breaking Changes | [`Win`](versions/Version_4.4/install_windows.ps1) \| [`Linux`](versions/Version_4.4/install_linux.sh) \| [`macOS`](versions/Version_4.4/install_macos.sh) |
| **[`versions/Version_4.5/`](versions/Version_4.5/)** | **v4.5** | **Bytecode Virtual Machine & `.crvc` Binary Compiler**: **High-Performance Stack-based VM (`CorvusVM`)**, **Compact Binary Executable Format (`.crvc`)**, **Bytecode Compiler (`corvus compile`)**, **Instruction Disassembler (`corvus dis`)**, **Direct VM Runner (`corvus --vm`)**, **First-Class Matrix Math `@` in Bytecode**, **Full Standalone & Portable SDK Bundles** | Tri-Engine Architecture: AST Tree-Walk Interpreter, Stack Bytecode Virtual Machine, and Ultra-Fast Native C99 Compiler | [`Win`](versions/Version_4.5/install_windows.ps1) \| [`Linux`](versions/Version_4.5/install_linux.sh) \| [`macOS`](versions/Version_4.5/install_macos.sh) |
| **[`versions/Version_4.6/`](versions/Version_4.6/)** | **v4.6** | **Enterprise Security Hardening, Robustness Engine & Automated Fuzzing**: **Zero `shell=True` Subprocess Execution**, **SSRF & Resource Bounds Enforcement (10MB Payload Limits, URL Scheme Whitelisting)**, **Safe SQLite Parameterization**, **HMAC-SHA256, SHA-512 & Secure Random Bytes**, **Hardened Bytecode Deserializer (Truncation & Bounds Protected)**, **Call Stack Depth & Stack Guard Rails (`MAX_STACK_DEPTH = 10000`)**, **Categorized Negative Test Suite (`test/`) & Automated Fuzzer (`test/fuzzer.py`)** | Hardened Tri-Engine Architecture: Secure AST Interpreter, Safe Stack Bytecode VM, and Optimized C99 Compiler | [`Win`](versions/Version_4.6/install_windows.ps1) \| [`Linux`](versions/Version_4.6/install_linux.sh) \| [`macOS`](versions/Version_4.6/install_macos.sh) |
| **[`versions/Version_4.7/`](versions/Version_4.7/)** | **v4.7** | **"RavenAI" Built-in AI Assistant & Transpiler**: **Interactive AI Chat Assistant (`corvus ai`)**, **Typo-Tolerant & Fuzzy Semantic Q&A (`corvus ai ask`)**, **Structural Code Explainer & AST Inspector (`corvus ai explain`)**, **Diagnostic Bug Analysis & Automatic Patch Synthesis (`corvus ai fix`)**, **Python-to-Corvus Code Transpiler (`corvus ai translate`)** | AI-Augmented Tri-Engine Architecture: Intelligent AST Interpreter, Bytecode VM, and C99 Native Compiler | [`Win`](versions/Version_4.7/install_windows.ps1) \| [`Linux`](versions/Version_4.7/install_linux.sh) \| [`macOS`](versions/Version_4.7/install_macos.sh) |


---

## 📖 The Story Behind Corvus

> *"I got inspired to build my own programming language after watching a video about a programmer who created G# and C#, and a video by AstroSam. Since I already knew Python, I decided to take on the challenge and build my very own programming language from scratch!"*  
> — **Saatvik Jain** (Creator of Corvus)

**Corvus** was born out of curiosity and a passion for computer science. Instead of relying on indentation (like Python) or curly braces (like C/JavaScript), Corvus introduces a unique syntax using **square brackets `[ ... ]` for code blocks**, reserving **curly braces `{ ... }` for native lists**. 

It has grown from an interpreted prototype into a **self-hosted, IR-optimized systems language** with native cross-platform assembly generation (`CorvusC`) that outputs standalone binary executables!

---

## 🚀 Quickstart & Master CLI Toolchain

### Prerequisites
* **Python 3.8+**
* Optional for Native Executable Compilation:
  ```powershell
  winget install NASM.NASM
  winget install MartinStorsjo.LLVM-MinGW.UCRT
  ```

---

### Master CLI Toolchain (`corvus` / `Corvus.py`)

#### 1. Running Programs & AI Matrix Multiplication (`@` Operator)
```bash
# Execute Corvus file with AST Interpreter
python Interpreter/Corvus.py Examples-and-Tests/17_matrix_matmul_suite.crv

# Native 2D lists, NumPy, PyTorch matrix multiplication using @:
# set lis; A = [[1, 2], [3, 4]]
# set lis; B = [[5, 6], [7, 8]]
# set any; C = A @ B  # -> [[19, 22], [43, 50]]
```

#### 2. Corvus Bytecode VM & `.crvc` Binary Compiler (v4.5)
```bash
# 1. Compile source into compact binary bytecode (.crvc)
corvus compile Examples-and-Tests/21_bytecode_vm_suite.crv -o app.crvc

# 2. Disassemble bytecode or source into human-readable instructions
corvus dis app.crvc

# 3. Execute directly with high-performance Corvus Bytecode VM
corvus app.crvc
# or execute source directly in VM mode
corvus --vm Examples-and-Tests/21_bytecode_vm_suite.crv
```


#### 3. Canonical Code Auto-Formatter (`corvus fmt`)
```bash
# Format a Corvus file in-place
python Interpreter/Corvus.py fmt myfile.crv

# CI/CD check mode (returns non-zero exit code if diff detected)
python Interpreter/Corvus.py fmt myfile.crv --check
```

#### 4. Test Runner Auto-Discovery (`corvus test`)
```bash
# Auto-discover and run all test suites (*test*.crv / *suite*.crv)
python Interpreter/Corvus.py test
```

#### 5. Strict Static Type Checker (`corvus --strict`)
```bash
# Validate types, undeclared variables, and function arity prior to execution
python Interpreter/Corvus.py --strict myfile.crv
```

#### 6. High-Precision Nanosecond Benchmarking (`corvus bench`)
```bash
# Measure execution time across 50 iterations with stats (mean, median, stdev)
python Interpreter/Corvus.py bench myfile.crv 100
```

#### 7. AST Statement & Node Profiler (`corvus profile`)
```bash
# Profile line-by-line execution count and hotspot bottlenecks
python Interpreter/Corvus.py profile myfile.crv
```

#### 8. CPM Package Manager Integration (`corvus install / list / remove`)
```bash
# Initialize a new project manifest
python Interpreter/Corvus.py init

# Install or list packages
python Interpreter/Corvus.py install math_utils
python Interpreter/Corvus.py list
```

#### 9. Diagnostic Explanations & Error Fixing
```bash
# Explain specific error code with verified fix examples
python Interpreter/Corvus.py --explain E0101

# Execute with AI diagnostic solutions
python Interpreter/Corvus.py myfile.crv --ai-fix
```

#### 7. AST Optimization Engine & Modern Syntax
```bash
# Execute with AST constant folding, algebraic simplification, and dead branch pruning
python Interpreter/Corvus.py myfile.crv --optimize

# Modern F-Strings and Inline Ternaries:
# set str; greeting = f"Hello {name}, score: {score * 2}"
# set str; grade = score >= 90 ? "A" : "B"
```

#### 8. High-Precision Benchmarking & AST Profiler
```bash
# Microbenchmark script execution time, ops/sec, and peak memory:
python Interpreter/Corvus.py bench myfile.crv 100

# Profile AST node execution frequency and statement breakdown:
python Interpreter/Corvus.py profile myfile.crv
```

#### 9. High-Performance C99 Native Transpiler (`-O3`)
```bash
# Transpile Corvus directly to portable C99 and compile to native optimized binary:
python Compiler/CorvusC_c.py myfile.crv -o myfile.exe -O3 --run
```

#### 10. Categorized Negative Testing & Automated Fuzzing Engine (`test/`)
Corvus includes a dedicated negative test suite and an automated fuzzing engine located in the `test/` directory to ensure all malformed, invalid, and structurally broken code is caught gracefully with clean `CorvusError` diagnostics rather than unhandled engine crashes:

```bash
# Run all 28 categorized negative tests (variables, conditions, loops, functions, oop, expressions)
python test/run_all_tests.py

# Run the automated fuzzer (stress-tests parser, evaluator, and bytecode compiler)
python test/fuzzer.py -n 100 -t 10

# Run standard test suites across language features
python Interpreter/Corvus.py test Examples-and-Tests
```

#### 11. RavenAI Built-in Developer Assistant & Transpiler (`corvus ai`)
Corvus v4.7 includes **RavenAI**, a native offline intelligent assistant specializing in Corvus syntax, code structural inspection, automated bug fixes, and Python-to-Corvus transpilation:

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

#### 12. Enterprise Ecosystem & Developer Tooling (`v5.0`)
Corvus v5.0 delivers the full **Enterprise Developer Ecosystem**:
```bash
# 1. RavenAI 2.0 Automated Unit Test Suite Generator
corvus ai testgen my_module.crv -o test_my_module.crv

# 2. Automated API & Markdown Documentation Generator
corvus ai doc my_module.crv -o API.md

# 3. Intelligent Code Review & Optimization Linting
corvus ai review my_module.crv

# 4. Reverse Transpiler (Corvus to Python or ISO C99)
corvus ai export my_module.crv --target py
corvus ai export my_module.crv --target c

# 5. CPM 2.0 Package Manager
corvus pkg init my_project
corvus pkg add https://github.com/user/lib.git
corvus pkg install
corvus pkg list

# 6. Interactive Terminal Tutorial (8 lessons with auto-grading)
corvus tour

# 7. Language Server Protocol (LSP) Daemon (VS Code / Neovim / Helix)
corvus lsp

# 8. WebAssembly Text (.wat) & HTML5 Browser Runner Export
corvus compile app.crv --target wasm -o app.wat
```

#### 13. Omni-Platform & Real-Time Ecosystem (`v5.1`)
Corvus v5.1 unlocks native performance, real-time networking, and creative tooling:
```bash
# 1. Tiered JIT Bytecode Acceleration (hotspot loop detection)
corvus --jit Examples-and-Tests/21_bytecode_vm_suite.crv

# 2. RavenAI 3.0 Natural Language Code Generation
corvus ai gen "Write a function to merge two sorted lists"

# 3. Automated Code Refactoring & Modernizer
corvus ai refactor legacy_code.crv

# 4. Asynchronous Channels & WebSockets
# get channel; set any; ch = channel.new(5)
# get web; set any; ws = web.ws_server(8081); ws.listen()

# 5. Playable 2D Games & Retro Audio Synthesizer
corvus Examples-and-Tests/games/flappy_crow.crv
corvus Examples-and-Tests/games/space_invaders.crv
corvus Examples-and-Tests/games/asteroids.crv

# 6. Embedded SQLite ORM & Reactive DataFrames
# get orm; set any; db = orm.open(":memory:")
# get dataframe; set any; df = dataframe.from_records([{"a": 1, "b": 2}])
```

#### 14. Deep Learning Neural AI & Cognitive Ecosystem (`v5.2`)
Corvus v5.2 equips developers with **RavenLM**, a real 166,464-parameter causal neural transformer language model:
```bash
# 1. Inspect RavenLM neural architecture & training loss
corvus ai model

# 2. Autoregressive neural code completion
corvus ai complete "mk func fibonacci(n) ["

# 3. Neural code generation from natural language prompt
corvus ai gen "multiply two matrices using native @ operator"

# 4. Retrain or fine-tune model on custom codebase
corvus ai train 25
```

---

## 🐛 Found a Bug?

We want Corvus to be as robust and developer-friendly as possible! If you encounter an unexpected error, crash, or parser failure, please **[open an issue on GitHub](https://github.com/mesaatvikjain-cyber/Corvus-Programming-Language/issues/new/choose)** using our automated issue template and include:

1. **Corvus version** (e.g. `v5.2`, `v5.1`, `v5.0`, `v4.7`, `v4.6`, `v4.5`, or `v4.4`)
2. **Operating system** (Windows, Linux, or macOS)
3. **Minimal `.crv` program** that reproduces the problem
4. **Expected behavior**
5. **Actual behavior**
6. **Error / output** (full terminal output or traceback)

---

## 📜 License & Author

- **Author**: Saatvik Jain
- **License**: MIT License
