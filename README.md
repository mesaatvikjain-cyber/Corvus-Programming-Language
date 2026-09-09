<p align="center">
  <img src="Documentation/corvus_logo.png" alt="Corvus Programming Language Logo" width="240"/>
</p>

<h1 align="center">Corvus Programming Language</h1>

<p align="center">
  <b>A modern, multi-version systems and application language featuring explicit block scoping <code>[ ... ]</code>, static type annotations, first-class lambdas, OOP, Three-Address Code (TAC) IR Optimization, Self-Hosted Compiler, Deterministic Scope Memory Ref-Counting, Interactive REPL, Super High-Level Optimization Engine, and VS Code Language Diagnostics.</b>
</p>

<p align="center">
  <a href="Documentation/webpage_corvus/index.html"><b>🌐 Documentation Webpage</b></a> •
  <a href="Documentation/INSTALLATION_GUIDE.md"><b>🛠️ Automated Installers Guide</b></a> •
  <a href="#-hands-on-version-tutorials"><b>📚 Version Tutorials</b></a> •
  <a href="Documentation/HOSTING.md"><b>☁️ Hosting Guide</b></a> •
  <a href="#-repository-version-sitemap">Version Sitemap</a> •
  <a href="#-the-story-behind-corvus">The Story</a>
</p>

---

## 🛠️ Automated Cross-Platform Installers (v1.1 - v4.1)

Corvus includes self-contained automated installer scripts for **Windows** (PowerShell), **Linux** (Bash), and **macOS** (Zsh/Bash) for **every single version release**!

### Quick One-Line Install Command
* **Windows (PowerShell Master Installer)**:
  ```powershell
  .\install_windows.ps1
  ```
* **Linux (Master Installer)**:
  ```bash
  bash install_linux.sh
  ```
* **macOS (Master Installer)**:
  ```bash
  bash install_macos.sh
  ```

For detailed version-by-version installation steps, see [Documentation/INSTALLATION_GUIDE.md](Documentation/INSTALLATION_GUIDE.md).

---

## 🌐 Official Documentation Website (`webpage_corvus`)

Corvus features a complete, interactive, self-contained **Master Documentation Website** located inside [`Documentation/webpage_corvus/`](Documentation/webpage_corvus/index.html) (and mirrored in [`docs/`](docs/index.html) for GitHub Pages).

### 🚀 Highlights of the Documentation Webpage
- **Interactive Version Tutorials (v1.1 - v4.1)**: Hands-on code walkthroughs with interactive tab selectors.
- **Language Syntax Quick Cheat Sheet**: Rapid reference cards for variables, control flow, functions, and OOP.
- **14 Exhaustive Chapters**: Covers Language Story, Syntax, Control Flow, Lambdas, OOP, Functional Pipelines, Ref-Counting Memory GC, "Murder of Crows" Concurrency, Native C FFI, Standard Library, TAC IR Compiler, v4.1 Super Optimizer, Self-Hosted Architecture, and VS Code Tooling.
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

---

## 📂 Repository Version Sitemap

The Corvus codebase is structured into explicit, standalone version releases so users and developers can select, compare, or run any generation of the language:

| Directory | Version | Core Features | Execution Engine | Installer Scripts |
| :--- | :--- | :--- | :--- | :--- |
| **[`Version_1.1/`](Version_1.1/)** | **v1.1** | Basic AST Interpreter, Lambdas, OOP, CPM Package Manager | Python AST Visitor Interpreter | [`Win`](Version_1.1/install_windows.ps1) \| [`Linux`](Version_1.1/install_linux.sh) \| [`macOS`](Version_1.1/install_macos.sh) |
| **[`Version_2.0/`](Version_2.0/)** | **v2.0** | Multi-Platform Native Assembly Compiler (`--target windows\|linux\|macos`), Pattern Matching, Pipeline Operator (`\|>`), Built-in Libs | NASM x86_64 Win64, ELF64, Mach-O Compiler & Interpreter | [`Win`](Version_2.0/install_windows.ps1) \| [`Linux`](Version_2.0/install_linux.sh) \| [`macOS`](Version_2.0/install_macos.sh) |
| **[`Version_3.0/`](Version_3.0/)** | **v3.0** | **Self-Hosted Compiler (`CorvusCompiler.crv`)**, **Three-Address Code (TAC) IR Optimizer**, **Ref-Counting GC**, **"Murder of Crows" 🐦 Concurrency Engine**, **Native C FFI** | Optimized TAC IR Compiler, Self-Hosted Corvus Compiler & Interpreter | [`Win`](Version_3.0/install_windows.ps1) \| [`Linux`](Version_3.0/install_linux.sh) \| [`macOS`](Version_3.0/install_macos.sh) |
| **[`Version_3.1/`](Version_3.1/)** | **v3.1** | **Enterprise Error Handling & Resilience Engine**: **Call Stack Tracebacks**, **Panic-Mode Parser Recovery**, **Assembly Runtime Panic Guards (`__corvus_panic_null`, `__corvus_panic_bounds`)** | Resilient Multi-Platform TAC IR Compiler & Enterprise Interpreter | [`Win`](Version_3.1/install_windows.ps1) \| [`Linux`](Version_3.1/install_linux.sh) \| [`macOS`](Version_3.1/install_macos.sh) |
| **[`Version_4.0/`](Version_4.0/)** | **v4.0** | **Native Corvus Standard Library Expansion (`math.crv`, `string.crv`, `file.crv`, `sys.crv`)**, **Advanced TAC IR Backend Optimizations**, **Interactive REPL Shell (`repl.py`)**, **VS Code Extension v0.3.0** | Full Enterprise TAC IR Compiler, Native Executable Compiler & Interactive REPL | [`Win`](Version_4.0/install_windows.ps1) \| [`Linux`](Version_4.0/install_linux.sh) \| [`macOS`](Version_4.0/install_macos.sh) |
| **[`Version_4.1/`](Version_4.1/)** | **v4.1** | **Super High-Level Optimization Engine**: **Constant Propagation**, **Algebraic Strength Reduction (`x * 2^n -> x << n`, `x / 2^n -> x >> n`)**, **Constant Branch Folding (`if (1)`)**, **CFG Jump Threading**, **Assembly Peephole Optimization** | Super-Optimized TAC IR Compiler & Native Executable Generator | [`Win`](Version_4.1/install_windows.ps1) \| [`Linux`](Version_4.1/install_linux.sh) \| [`macOS`](Version_4.1/install_macos.sh) |

---

## 📖 The Story Behind Corvus

> *"I got inspired to build my own programming language after watching a video about a programmer who created G# and C#, and a video by AstroSam. Since I already knew Python, I decided to take on the challenge and build my very own programming language from scratch!"*  
> — **Saatvik Jain** (Creator of Corvus)

**Corvus** was born out of curiosity and a passion for computer science. Instead of relying on indentation (like Python) or curly braces (like C/JavaScript), Corvus introduces a unique syntax using **square brackets `[ ... ]` for code blocks**, reserving **curly braces `{ ... }` for native lists**. 

It has grown from an interpreted prototype into a **self-hosted, IR-optimized systems language** with native cross-platform assembly generation (`CorvusC`) that outputs standalone binary executables!

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

#### Launching the Interactive REPL Shell (v4.1)
```bash
python Version_4.1/Interpreter/Corvus.py --repl
```

#### Running Version 4.1 Super Optimization Test Suite
```bash
# Interpreter
python Version_4.1/Interpreter/Corvus.py Version_4.1/Examples-and-Tests/13_super_optimization_suite.crv

# Native Windows Executable Compiler
python Version_4.1/Compiler_Windows/CorvusC_win64.py Version_4.1/Examples-and-Tests/13_super_optimization_suite.crv
```

---

## 📜 License & Author

- **Author**: Saatvik Jain
- **License**: MIT License
