# Corvus Version 5.0 Standalone & Portable Distribution

Welcome to the official **Zero-Dependency Distribution Packages** for the **Corvus Programming Language (v5.0 — Enterprise Ecosystem)**.

---

## 📦 Distribution Packages Overview

Corvus v5.0 introduces **RavenAI 2.0**, **CPM 2.0 Package Manager**, **Native Micro Web Framework**, **Interactive CLI Tour**, **Language Server Protocol (LSP)**, and **WebAssembly (Wasm) Compilation**:

### 🌟 Tier 1: Standalone Single-File Executables (`standalone/`)
* **`standalone/corvus.exe`** — The complete Corvus v5.0 engine:
  - **RavenAI 2.0**: Unit test generator (`testgen`), doc generator (`doc`), code reviewer (`review`), bidirectional transpiler (`translate`, `export`), and interactive assistant (`chat`).
  - **CPM 2.0**: Package manager commands (`pkg init`, `add`, `install`, `list`).
  - **Language Server Protocol**: Built-in JSON-RPC LSP daemon (`corvus lsp`).
  - **Interactive Tour**: 8 guided in-terminal lessons (`corvus tour`).
  - **Wasm Compiler**: `corvus compile <file.crv> --target wasm`.
  - **Bytecode Virtual Machine**: Compact `.crvc` binary stack machine execution.
  - **C99 Native Compiler**: Zero-dependency optimized machine binary generation.

#### Instant Installation:
* **Windows**: Run `.\install_standalone_windows.ps1`
* **Linux**: Run `bash install_standalone_linux.sh`
* **macOS**: Run `bash install_standalone_macos.sh`

---

### 🧰 Tier 2: All-in-One Portable SDK (`portable-sdk/`)
* Contains full toolchain, all standard libraries (`StdLib/`), `Interpreter/`, and native runners.

---

## 🚀 Quick Verification Commands

```bash
# 1. Start interactive tutorial
corvus tour

# 2. Generate unit tests automatically
corvus ai testgen Examples-and-Tests/02_recursion_factorial.crv

# 3. Generate documentation automatically
corvus ai doc Examples-and-Tests/04_classes_and_oop.crv

# 4. Review code for performance optimizations
corvus ai review Examples-and-Tests/17_matrix_matmul_suite.crv

# 5. Compile to WebAssembly
corvus compile Examples-and-Tests/01_hello_and_input.crv --target wasm
```
