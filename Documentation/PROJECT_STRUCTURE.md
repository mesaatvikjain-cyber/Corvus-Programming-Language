# 🧭 Corvus Repository Architecture & Directory Guide

Welcome to the Corvus codebase! This guide is designed to help contributors, users, and language researchers easily navigate the directory layout and understand how the various components and execution engines interact.

---

## 🏛️ High-Level Directory Overview

```text
Corvus/
├── Interpreter/          # 🌟 Primary AST Interpreter, REPL, and Developer Toolchain
├── Compiler/             # ⚡ Primary C99 Native Compiler driver (-O3 pipeline)
├── Compiler_Core/        # 🧩 Shared Compiler Components (Lexer, Parser, C Transpiler)
├── Compiler_Windows/     # 🪟 Windows x86_64 NASM Assembly Compiler backend
├── Compiler_Linux/       # 🐧 Linux x86_64 NASM Assembly Compiler backend
├── Compiler_MacOS/       # 🍏 macOS Mach-O NASM Assembly Compiler backend
├── StdLib/               # 📚 30+ Standard Library modules (.crv and native bridges)
├── Distributions/        # 📦 Zero-Dependency Standalone Executables & Portable SDKs
│   ├── Version_4.4/      # Distribution bundle for v4.4
│   └── Version_4.5/      # Distribution bundle for v4.5 (Bytecode VM & Compiler)
├── Documentation/        # 📖 Master Documentation, Tutorials, and Web Docs source
│   ├── tutorials/        # Markdown tutorials for v1.1 through v4.5
│   ├── webpage_corvus/   # Interactive Master Documentation Website source
│   ├── INSTALLATION_GUIDE.md # Cross-platform installation instructions
│   └── HOSTING.md        # Hosting guide for GitHub Pages, Vercel, Netlify
├── docs/                 # 🌐 GitHub Pages mirror of the documentation website
├── Examples-and-Tests/   # 🧪 Test suites and real-world example programs
├── Editor-Extension/     # 💻 Visual Studio Code syntax & language diagnostics extension
├── bin/                  # 🚀 Command-line wrapper scripts (corvus, corvusc)
├── Version_1.1/ to 4.5/  # 📜 Self-contained historical release snapshots
├── install_windows.ps1   # 🪟 Interactive master Windows installer (all versions)
├── install_linux.sh      # 🐧 Interactive master Linux installer (all versions)
├── install_macos.sh      # 🍏 Interactive master macOS installer (all versions)
└── README.md             # 📖 Master project overview and quickstart
```

---

## ⚙️ The Tri-Engine Execution Model

Corvus offers three distinct, complementary execution pipelines:

| Pipeline | Entry Command | Core Components | Best For |
| :--- | :--- | :--- | :--- |
| **1. AST Interpreter** | `corvus app.crv` | `Interpreter/Corvus.py`, `evaluatorcorvus.py` | Rapid prototyping, interactive REPL, rich `--ai-fix` diagnostics |
| **2. Stack Bytecode VM** | `corvus --vm app.crv`<br>`corvus compile app.crv`<br>`corvus app.crvc` | `Interpreter/bytecode.py`, `compiler_vm.py`, `vm.py` | High throughput, compact portable binary `.crvc` distribution, disassembling |
| **3. Native C99 Compiler** | `corvusc app.crv -o app.exe` | `Compiler/CorvusC_c.py`, `Compiler_Core/` | Maximum raw performance, standalone zero-runtime binary deployment (`-O3`) |

---

## 📁 Key Directories in Detail

### 1. `Interpreter/`
The primary development and execution driver for Corvus:
* `Corvus.py`: Master CLI entry point (`corvus`). Dispatches commands (`compile`, `dis`, `--vm`, `bench`, `profile`, `fmt`, `test`).
* `lexercorvus.py`: Dual-syntax tokenizer supporting both mainstream `{ ... }` / `[ ... ]` and classic Corvus bracket inversions.
* `parsercorvus.py`: Recursive-descent AST generator with smart type inference and optional semicolons.
* `evaluatorcorvus.py`: AST tree-walk runtime environment with lexical scoping and class dispatch.
* `bytecode.py`: Opcode definitions, bytecode chunk structure, binary serialization (`.crvc`), and disassembler.
* `compiler_vm.py`: Compiles high-level Corvus AST nodes directly into linear bytecode chunks.
* `vm.py`: Stack-based virtual machine with activation call frames and native matrix `@` multiplication.
* `ast_optimizer.py`: High-level AST optimization pass (constant folding, algebraic simplification, dead branch pruning).
* `errors.py`: Rust-style diagnostic error system with `--explain <CODE>` and Levenshtein typo correction heuristics.

### 2. `Compiler/` & `Compiler_Core/`
The native compilation pipeline:
* `Compiler/CorvusC_c.py`: Transpiles Corvus AST into standard C99, then links with Clang/GCC using `-O3` optimizations.
* `Compiler_Core/c_transpiler.py`: Core emitter mapping Corvus types, lists, dictionaries, matrices, and functions to C99.
* `Compiler_Windows/`, `Compiler_Linux/`, `Compiler_MacOS/`: Platform-specific NASM x86_64 assembly backends.

### 3. `StdLib/`
Standard libraries accessible via `get <module>`:
* **AI / ML Stack**: `numpy.crv`, `torch.crv`, `tensorflow.crv`, `pandas.crv`, `scikit_learn.crv`, `transformers.crv`.
* **Graphics & Games**: `graphics.crv` (zero-dependency desktop 2D canvas).
* **System & Utilities**: `math.crv`, `string.crv`, `file.crv`, `sys.crv`, `json.crv`, `crypto.crv`, `socket.crv`.

### 4. `Distributions/`
Pre-packaged standalone bundles for end users who do not have Python installed:
* **`Version_4.5/`**:
  * `standalone/`: Contains single-file standalone binaries `corvus.exe` and `corvusc.exe`.
  * `portable-sdk/`: Full portable Corvus development kit with `bin/corvus.bat` and `bin/corvusc.bat`.
  * `install_standalone_windows.ps1`: One-click PATH installer.

### 5. `Documentation/` & `docs/`
* `Documentation/tutorials/`: 10 comprehensive version tutorials spanning v1.1 up to v4.5.
* `Documentation/webpage_corvus/`: Canonical HTML/CSS/JS source of the master interactive documentation website.
* `docs/`: Deployment target for GitHub Pages hosting.

### 6. `Version_1.1/` through `Version_4.5/`
Stand-alone snapshots preserving each evolutionary generation of Corvus. Each directory has its own dedicated interpreter, compiler, test suite, and platform installers for reproducibility and regression testing.

---

## 🛠️ Typical Developer Workflows

### Run the AST Interpreter
```bash
python Interpreter/Corvus.py Examples-and-Tests/01_basic_syntax.crv
```

### Compile and Run via Bytecode VM
```bash
# Compile to binary bytecode
python Interpreter/Corvus.py compile Examples-and-Tests/21_bytecode_vm_suite.crv -o suite.crvc

# Disassemble
python Interpreter/Corvus.py dis suite.crvc

# Execute on the VM
python Interpreter/Corvus.py suite.crvc
```

### Compile to Native C99 Executable
```bash
python Compiler/CorvusC_c.py Examples-and-Tests/07_compiler_parity_test.crv -o test_app.exe --run
```

### Run Multi-Version Test Audit
```bash
python scratch/audit_all_versions.py
```
