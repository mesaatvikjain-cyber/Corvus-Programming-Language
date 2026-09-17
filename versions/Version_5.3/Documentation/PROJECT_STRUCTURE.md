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
├── test/                 # 🧪 Categorized Negative Test Suite & Grammar-Aware Fuzzer
├── Distributions/        # 📦 Zero-Dependency Standalone Executables & Portable SDKs
│   ├── Version_4.4/      # Distribution bundle for v4.4
│   ├── Version_4.5/      # Distribution bundle for v4.5 (Bytecode VM & Compiler)
│   ├── Version_4.6/      # Distribution bundle for v4.6 (Security Hardened & VM)
│   ├── Version_4.7/      # Distribution bundle for v4.7 (RavenAI & Hardened VM)
│   ├── Version_5.0/      # Distribution bundle for v5.0 (Enterprise Ecosystem)
│   ├── Version_5.1/      # Distribution bundle for v5.1 (Omni-Platform & Real-Time Ecosystem)
│   └── Version_5.2/      # Distribution bundle for v5.2 (Deep Learning Neural AI Ecosystem)
├── Documentation/        # 📖 Master Documentation, Tutorials, and Web Docs source
│   ├── tutorials/        # Markdown tutorials for v1.1 through v5.2
│   ├── webpage_corvus/   # Interactive Master Documentation Website source
│   ├── INSTALLATION_GUIDE.md # Cross-platform installation instructions
│   └── HOSTING.md        # Hosting guide for GitHub Pages, Vercel, Netlify
├── docs/                 # 🌐 GitHub Pages mirror of the documentation website
├── Examples-and-Tests/   # 🧪 Test suites, playable retro games, and example programs
├── Editor-Extension/     # 💻 Visual Studio Code syntax & language diagnostics extension
├── bin/                  # 🚀 Command-line wrapper scripts (corvus, corvusc)
├── versions/             # 📜 Standalone release snapshots (v1.1 through v5.2)
│   ├── Version_1.1/      # Reference AST visitor interpreter & OOP
│   ├── Version_2.0/      # Multi-platform NASM assembly compiler
│   ├── Version_3.0/      # Self-hosted compiler & "Murder of Crows" concurrency
│   ├── Version_3.1/      # Visual stack tracebacks & panic-mode recovery
│   ├── Version_4.0/      # Native standard library expansion & REPL
│   ├── Version_4.1/      # Super high-level IR optimization engine
│   ├── Version_4.2/      # Desktop 2D graphics canvas & event loop
│   ├── Version_4.3/      # AI/ML suite, 30+ stdlib modules & diagnostics
│   ├── Version_4.4/      # Modern dual bracket syntax & smart type inference
│   ├── Version_4.5/      # Corvus Bytecode VM & .crvc binary compiler
│   ├── Version_4.6/      # Enterprise Security Hardening & Robustness Engine
│   ├── Version_4.7/      # "RavenAI" Built-in Assistant, Transpiler & Hardened VM
│   ├── Version_5.0/      # Enterprise Ecosystem: RavenAI 2.0, CPM, Web, Tour, LSP, Wasm
│   ├── Version_5.1/      # Omni-Platform: JIT Engine, WebSockets, Channels, GameKit, ORM, DataFrames
│   └── Version_5.2/      # Neural AI: RavenLM Transformer, Autoregressive Completion, In-Tree Training
├── install_windows.ps1   # 🪟 Interactive master Windows installer (all versions)
├── install_linux.sh      # 🐧 Interactive master Linux installer (all versions)
├── install_macos.sh      # 🍏 Interactive master macOS installer (all versions)
└── README.md             # 📖 Master project overview and quickstart
```

---

## ⚙️ The Omni-Platform Execution Model

Corvus offers four distinct, complementary execution pipelines:

| Pipeline | Entry Command | Core Components | Best For |
| :--- | :--- | :--- | :--- |
| **1. AST Interpreter** | `corvus app.crv` | `Interpreter/Corvus.py`, `evaluatorcorvus.py` | Rapid prototyping, interactive REPL, rich `--ai-fix` diagnostics |
| **2. Tiered JIT VM** | `corvus --jit app.crv` | `Interpreter/jit_engine.py`, `vm.py` | Hotspot loop acceleration, matrix & math heavy algorithms |
| **3. Stack Bytecode VM** | `corvus --vm app.crv`<br>`corvus compile app.crv`<br>`corvus app.crvc` | `Interpreter/bytecode.py`, `compiler_vm.py`, `vm.py` | High throughput, compact portable binary `.crvc` distribution, disassembling |
| **4. Native C99 Compiler** | `corvusc app.crv -o app.exe` | `Compiler/CorvusC_c.py`, `Compiler_Core/` | Maximum raw performance, standalone zero-runtime binary deployment (`-O3`) |

---

## 📁 Key Directories in Detail

### 1. `Interpreter/`
The primary development and execution driver for Corvus:
* `Corvus.py`: Master CLI entry point (`corvus`). Dispatches commands (`compile`, `dis`, `--vm`, `--jit`, `bench`, `profile`, `fmt`, `test`, `ai`, `pkg`, `tour`, `lsp`).
* `lexercorvus.py`: Dual-syntax tokenizer supporting both mainstream `{ ... }` / `[ ... ]` and classic Corvus bracket inversions.
* `parsercorvus.py`: Recursive-descent AST generator with smart type inference, expression conditionals, and optional semicolons.
* `evaluatorcorvus.py`: AST tree-walk runtime environment with lexical scoping and class dispatch.
* `jit_engine.py`: Dynamic JIT hotspot loop detector and bytecode optimizer.
* `raven_model.py`: Causal Autoregressive Decoder Transformer (`RavenLM`), Multi-Head Attention, and Dual PyTorch/NumPy runtime.
* `train_raven.py`: Automated codebase corpus harvester, tokenizer, AdamW training loop, and weight exporter.
* `raven_weights.pt`: Pre-trained PyTorch neural model checkpoint (166,464 weights).
* `raven_weights.json`: Portable JSON neural weights for zero-dependency standalone execution.
* `raven_vocab.json`: Learned character and syntax token vocabulary.
* `bytecode.py`: Opcode definitions, bytecode chunk structure, binary serialization (`.crvc`), and disassembler.
* `compiler_vm.py`: Compiles high-level Corvus AST nodes directly into linear bytecode chunks.
* `vm.py`: Stack-based virtual machine with activation call frames and native matrix `@` multiplication.
* `ast_optimizer.py`: High-level AST optimization pass (constant folding, algebraic simplification, dead branch pruning).
* `errors.py`: Rust-style diagnostic error system with `--explain <CODE>` and Levenshtein typo correction heuristics.
* `ai_engine.py`: RavenAI 4.0 Neural Assistant (`complete`, `model`, `train`, `gen`, `refactor`, `testgen`, `doc`, `review`, `export`, `ask`, `explain`, `fix`, `translate`).
* `package_manager.py`: CPM 2.0 package manager engine resolving `corvus.json` and `corvus.lock`.
* `lsp_server.py`: Microsoft JSON-RPC 2.0 Language Server Protocol daemon (`corvus lsp`).
* `tour.py`: Interactive 8-lesson terminal tutorial engine (`corvus tour`).
* `std_web.py`: Native zero-dependency micro HTTP web framework & WebSocket server (`web.server()`, `web.ws_server()`).
* `std_channel.py`: Thread-safe asynchronous channel primitive (`channel.new()`).
* `std_gamekit.py`: 2D vectors, circle/box colliders, and particle emitters (`gamekit`).
* `std_audio.py`: Zero-dependency retro square/sine wave sound & chord synthesizer (`audio`).
* `std_orm.py`: Lightweight active-record SQLite ORM (`orm`).
* `std_dataframe.py`: Pure standard library reactive DataFrames (`dataframe`).
* `wasm_backend.py`: WebAssembly Text Format (`.wat`) emitter and HTML5 browser runner generator.

### 2. `Compiler/` & `Compiler_Core/`
The native compilation pipeline:
* `Compiler/CorvusC_c.py`: Transpiles Corvus AST into standard C99, then links with Clang/GCC using `-O3` optimizations.
* `Compiler_Core/c_transpiler.py`: Core emitter mapping Corvus types, lists, dictionaries, matrices, and functions to C99.
* `Compiler_Windows/`, `Compiler_Linux/`, `Compiler_MacOS/`: Platform-specific NASM x86_64 assembly backends.

### 3. `StdLib/`
Standard libraries accessible via `get <module>`:
* **Real-Time & Networking**: `corvus_web.crv` (HTTP & WebSockets), `channel.crv` (Async Channels), `net.crv`.
* **Gaming & Creative**: `gamekit.crv` (2D Physics & Particles), `audio.crv` (Retro Sound Synthesizer), `graphics.crv` (2D Canvas).
* **Data & Persistence**: `orm.crv` (Active-Record SQLite ORM), `dataframe.crv` (DataFrames), `sqlite.crv`, `csv.crv`, `json.crv`.
* **AI / ML Stack**: `numpy.crv`, `torch.crv`, `tensorflow.crv`, `pandas.crv`, `scikit_learn.crv`, `transformers.crv`.
* **System & Utilities**: `math.crv`, `string.crv`, `file.crv`, `sys.crv`, `crypto.crv`, `collections.crv`.

### 4. `Distributions/`
Pre-packaged standalone bundles for end users who do not have Python installed:
* **`Version_5.2/`**, **`Version_5.1/`**, **`Version_5.0/`**, **`Version_4.7/`**, **`Version_4.6/`** & **`Version_4.5/`**:
  * `standalone/`: Contains single-file standalone binaries `corvus.exe` and `corvusc.exe`.
  * `portable-sdk/`: Full portable Corvus development kit with `bin/corvus.bat`, `bin/corvusc.bat`, and pre-trained neural model weights.
  * `install_standalone_windows.ps1`: One-click PATH installer.

### 5. `Documentation/` & `docs/`
* `Documentation/tutorials/`: 15 comprehensive version tutorials spanning v1.1 up to v5.2.
* `Documentation/webpage_corvus/`: Canonical HTML/CSS/JS source of the master interactive documentation website.
* `docs/`: Deployment target for GitHub Pages hosting with In-Browser Wasm Playground.

### 6. `versions/` (`Version_1.1/` through `Version_5.2/`)
Dedicated directory grouping all 13 historical release snapshots of Corvus. Each version snapshot is fully isolated with its own dedicated interpreter, compiler, test suite, and platform installers for reproducibility, educational reference, and regression testing.

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
