# Corvus Version 5.1 Standalone & Portable Distribution

Welcome to the official **Zero-Dependency Distribution Packages** for the **Corvus Programming Language (v5.1 — Omni-Platform & Real-Time Ecosystem)**.

---

## 📦 Distribution Packages Overview

Corvus v5.1 introduces the **Tiered JIT Execution Engine**, **Real-Time WebSockets & Async Channels**, **Interactive Wasm Playground & IDE**, **RavenAI 3.0 Code Generation & Refactoring**, **2D GameKit & Retro Audio Synthesizer**, and **Active-Record SQLite ORM & Reactive DataFrames**:

### 🌟 Tier 1: Standalone Single-File Executables (`standalone/`)
* **`standalone/corvus.exe`** — The complete Corvus v5.1 engine:
  - **Tiered JIT Engine**: Dynamic hotspot loop execution (`corvus --jit <file.crv>`).
  - **RavenAI 3.0**: Natural language prompt code generation (`gen`), code refactoring (`refactor`), unit tests (`testgen`), doc generator (`doc`), code review (`review`), bidirectional transpiler (`translate`, `export`).
  - **CPM 2.0**: Decentralized package manager (`pkg init`, `add`, `install`, `list`).
  - **Micro Web & WebSockets**: Embedded HTTP REST server and WebSocket server daemon.
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
# 1. Tiered JIT Acceleration
corvus --jit Examples-and-Tests/21_bytecode_vm_suite.crv

# 2. Run Comprehensive v5.1 Omni-Platform Suite
corvus Examples-and-Tests/23_v5.1_omni_ecosystem_suite.crv

# 3. Generate Corvus code from natural language prompt
corvus ai gen "Write a function to reverse a list"

# 4. Play Retro Flappy Crow Game
corvus Examples-and-Tests/games/flappy_crow.crv
```
