# Corvus Version 4.7 Standalone & Portable Distribution

Welcome to the official **Zero-Dependency Distribution Packages** for the **Corvus Programming Language (v4.7)**.

---

## 📦 Distribution Packages Overview

Corvus v4.7 introduces **RavenAI** — a built-in, 100% offline intelligent developer assistant, code explainer, auto-fixer, and Python-to-Corvus transpiler, alongside the high-performance **Corvus Bytecode Virtual Machine (CorvusVM)** and native C99 compiler:

### 🌟 Tier 1: Standalone Single-File Executables (`standalone/`)
* **`standalone/corvus.exe`** — The complete Corvus v4.7 engine:
  - **RavenAI Assistant**: Built-in typo-tolerant Q&A (`ask`), structural explainer (`explain`), auto-fixer (`fix`), Python transpiler (`translate`), and interactive assistant (`chat`).
  - **Bytecode Virtual Machine**: Fast stack machine executing `.crvc` binary bytecode.
  - **Bytecode Compiler**: `corvus compile <app.crv> [-o app.crvc]`.
  - **Bytecode Disassembler**: `corvus dis <app.crv | app.crvc>`.
  - **AST Interpreter & REPL**: Direct execution with full runtime debugging and `--ai-fix`.
  - **Toolchain Suite**: canonical formatter (`fmt`), test runner (`test`), nanosecond benchmarker (`bench`), and profiler (`profile`).
* **`standalone/corvusc.exe`** — The complete Corvus v4.7 C99 Native Compiler driver with `-O3` pipeline optimization passes.
* **Key Benefits**:
  - **Zero Python Installation Required**: Works immediately on any fresh Windows system.
  - **Single Portable File**: Drop `corvus.exe` into any folder or USB drive.

#### Instant Installation:
* **Windows**: Run `.\install_standalone_windows.ps1` to automatically add `standalone\` to your User PATH.
* **Linux**: Run `bash install_standalone_linux.sh`
* **macOS**: Run `bash install_standalone_macos.sh`

---

### 🧰 Tier 2: All-in-One Portable SDK (`portable-sdk/`)
* Contains the full source-level Corvus toolchain:
  - `bin/corvus.bat` and `bin/corvusc.bat` (Windows)
  - `bin/corvus` and `bin/corvusc` (Linux / macOS)
  - `StdLib/` (30+ Standard Library modules including AI/ML, graphics, networking, and crypto)
  - `Examples-and-Tests/` (test suites and interactive examples)
  - `runtime/setup_embedded_python.ps1` (Optional one-click embedded Python bootstrapper for 100% offline isolated environments)

#### How Portable SDK Launchers Work:
1. First, checks if an embedded Python runtime is located in `runtime/python.exe`.
2. If not found, seamlessly runs with system Python from PATH.
3. If neither is found, displays actionable setup instructions or runs the embedded bootstrapper.

---

## 🚀 Quick CLI Verification (v4.7 Features)

### 1. Ask RavenAI (Typo-Tolerant Knowledge Base)
```bash
corvus ai ask "how to define a funtion?"
```

### 2. Structural Code Explainer
```bash
corvus ai explain Examples-and-Tests/01_hello_and_input.crv
```

### 3. Syntax Diagnostic & Auto-Fixer
```bash
corvus ai fix "def greet(name): print('Hello', name)"
```

### 4. Transpile Python to Corvus
```bash
corvus ai translate script.py
```

### 5. Interactive RavenAI REPL
```bash
corvus ai chat
```

### 6. Compile to Compact Binary Bytecode (`.crvc`)
```bash
corvus compile Examples-and-Tests/21_bytecode_vm_suite.crv -o suite.crvc
```

### 7. Run on Corvus Bytecode VM
```bash
corvus suite.crvc
# or directly from source
corvus --vm Examples-and-Tests/21_bytecode_vm_suite.crv
```

### 8. Compile to Native C99 Executable
```bash
corvusc Examples-and-Tests/21_bytecode_vm_suite.crv -o suite.exe --run
```
