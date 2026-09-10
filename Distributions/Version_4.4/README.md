# Corvus Version 4.4 Standalone & Portable Distribution

Welcome to the official **Zero-Dependency Distribution Packages** for the **Corvus Programming Language (v4.4)**.

---

## 📦 Distribution Packages Overview

Corvus v4.4 provides multiple tiers of distribution so developers can select the workflow that best suits their needs:

### 🌟 Tier 1: Standalone Single-File Executables (`standalone/`)
* **`standalone/corvus.exe`** — The complete Corvus v4.4 AST Interpreter, REPL, Code Formatter (`fmt`), Test Runner (`test`), Benchmarker (`bench`), Profiler (`profile`), and CPM package tool.
* **`standalone/corvusc.exe`** — The complete Corvus v4.4 C99 Native Compiler driver with `-O3` pipeline optimization passes.
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

## 🚀 Quick CLI Verification

### Running Corvus Interpreter
```bash
corvus --help
corvus Examples-and-Tests/20_v4.4_modern_ergonomics_suite.crv
corvus --repl
```

### Compiling to Native Executables
```bash
corvusc Examples-and-Tests/20_v4.4_modern_ergonomics_suite.crv -o my_app.exe --run
```
