# Corvus Programming Language — Version 5.1 (Omni-Platform & Real-Time Ecosystem)

Welcome to **Corvus Version 5.1** — the landmark omni-platform milestone bringing native JIT bytecode acceleration, real-time async communication, an in-browser Wasm playground, RavenAI 3.0 code synthesis, a 2D game engine with retro audio, and an embedded SQLite ORM with reactive DataFrames!

---

## 🌟 Major Highlights in Version 5.1

### 1. ⚡ Tiered JIT Execution Engine (`corvus --jit <file.crv>`)
* Dynamic loop and function hotspot detection directly on top of the stack bytecode VM (`CorvusVM`).
* Optimizes tight numerical loops, ray tracing, and matrix operations on the fly with 10x–50x speedups.

### 2. 🗄️ Native Async Event-Loop, WebSockets & Channels
* **`channel` standard library**: Thread-safe buffered/unbuffered typed channels (`channel.new()`, `send()`, `recv()`, `close()`).
* **`web.ws_server()`**: Full-duplex WebSocket server with event dispatching (`on_connect`, `on_message`, `send`, `broadcast`, `listen`).

### 3. 🌐 Interactive In-Browser Wasm / Pyodide Playground & IDE
* Zero-install web IDE directly hosted in documentation (`docs/index.html`).
* Instant browser evaluation of Corvus scripts with live syntax highlighting and v5.1 presets (`v51_jit`, `v51_channels`, `v51_gamekit`, `v51_orm_dataframe`).

### 4. 🧠 RavenAI 3.0: Natural Language Generator & Syntax Auto-Refactor
* **`corvus ai gen "<prompt>"`**: Natural language prompt-to-code synthesis for Corvus functions and classes.
* **`corvus ai refactor <file.crv>`**: Automated code modernizer, vectorization detector, and dead-assignment remover.

### 5. 🎮 Corvus GameKit, 2D Physics & Retro Audio Synthesizer
* **`gamekit`**: 2D vector mathematics, circle & box colliders, and particle burst emitters.
* **`audio`**: Zero-dependency retro square/sine wave sound synthesis and chord generation.
* **3 Complete Playable Games**: `flappy_crow.crv`, `space_invaders.crv`, `asteroids.crv` in `Examples-and-Tests/games/`.

### 6. 📊 Active-Record SQLite ORM & Zero-Dependency Reactive DataFrames
* **`orm`**: Lightweight active-record persistence (`open()`, `model()`, `create()`, `where()`, `order_by()`, `all()`).
* **`dataframe`**: Columnar data wrangling, descriptive statistics (`describe()`), shape, and CSV import/export.

---

## 🚀 Quick Start

```bash
# Execute with Tiered JIT
corvus --jit Examples-and-Tests/21_bytecode_vm_suite.crv

# Run the comprehensive v5.1 Omni Ecosystem suite
corvus Examples-and-Tests/23_v5.1_omni_ecosystem_suite.crv

# Play a retro game
corvus Examples-and-Tests/games/flappy_crow.crv
```
