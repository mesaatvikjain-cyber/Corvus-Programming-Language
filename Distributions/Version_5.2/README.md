# Corvus Version 5.2 Standalone & Portable Distribution

Welcome to the official **Zero-Dependency Distribution Packages** for the **Corvus Programming Language (v5.2 — Deep Learning Neural AI & Cognitive Ecosystem)**.

---

## 📦 Distribution Packages Overview

Corvus v5.2 introduces **RavenLM (Real Neural Transformer Language Model)**, **Autoregressive Neural Code Completion**, **In-Tree Fine-Tuning Pipeline**, alongside the **Tiered JIT Engine**, **Real-Time WebSockets & Channels**, **2D GameKit & Audio Synthesizer**, and **Active-Record SQLite ORM & DataFrames**:

### 🌟 Tier 1: Standalone Single-File Executables (`standalone/`)
* **`standalone/corvus.exe`** — The complete Corvus v5.2 engine:
  - **RavenLM Neural Transformer**: Causal 3-layer autoregressive decoder (`corvus ai model`, `complete`, `gen`, `train`).
  - **Tiered JIT Engine**: Dynamic hotspot loop acceleration (`corvus --jit <file.crv>`).
  - **CPM 2.0**: Decentralized package manager (`pkg init`, `add`, `install`, `list`).
  - **Micro Web & WebSockets**: Embedded HTTP REST server and WebSocket daemon.
  - **Language Server Protocol**: Built-in JSON-RPC LSP daemon (`corvus lsp`).
  - **Bytecode Virtual Machine**: Compact `.crvc` binary stack machine execution.
  - **C99 Native Compiler**: Zero-dependency optimized machine binary generation.

#### Instant Installation:
* **Windows**: Run `.\install_standalone_windows.ps1`
* **Linux**: Run `bash install_standalone_linux.sh`
* **macOS**: Run `bash install_standalone_macos.sh`

---

### 🧰 Tier 2: All-in-One Portable SDK (`portable-sdk/`)
* Contains full toolchain, pre-trained neural weights (`raven_weights.pt`, `raven_weights.json`), all standard libraries (`StdLib/`), `Interpreter/`, and native runners.
