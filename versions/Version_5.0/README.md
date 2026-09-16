# Corvus Programming Language — Version 5.0 (Enterprise Ecosystem)

Welcome to **Corvus Version 5.0** — the landmark release that transforms Corvus from a programming language into an enterprise developer ecosystem!

---

## 🌟 Major Highlights in Version 5.0

### 1. 🤖 RavenAI 2.0 (Offline Intelligent Developer Tooling)
* **Automated Unit Test Generator (`corvus ai testgen <file.crv> [-o out]`)**:
  - Automatically inspects all declared functions (`mk func`), parses parameters, and synthesizes runnable assertion test suites with standard invocations and zero/boundary tests.
* **Automated Documentation Generator (`corvus ai doc <file.crv> [-o out.md]`)**:
  - Extracts module overviews, classes (`cls`), fields, methods, top-level functions, and dependencies into GitHub-ready Markdown tables.
* **Static Code Review & Quality Linter (`corvus ai review <file.crv>`)**:
  - Analyzes code quality: identifies nested loops eligible for the native `@` matrix operator, detects unused assigned variables, flags division without zero guards, and warns of deep nesting.
* **Bidirectional Reverse Transpiler (`corvus ai export <file.crv> [--target py|c]`)**:
  - Transpiles Corvus source code back into Python or ISO C99.
* **Interactive Terminal Assistant (`corvus ai [chat]`)**:
  - Interactive REPL supporting `code--ask`, `code--summary`, `code--fix`, `code--translate`, `code--testgen`, `code--doc`, `code--review`, `code--export`.

---

### 2. 📦 CPM 2.0 (Official Decentralized Package Manager)
* **`corvus pkg init [name]`**: Creates a standardized `corvus.json` project manifest.
* **`corvus pkg add <git_url | pkg>`**: Clones/downloads packages from Git repositories or ZIP archives directly into `crv_modules/`, generating `corvus.lock`.
* **`corvus pkg install`**: One-command resolution and installation of all declared dependencies.
* **`corvus pkg list`**: Formatted inspection of installed packages and resolved paths.

---

### 3. 🌐 Native Micro Web Framework (`web` / `StdLib/corvus_web.crv`)
* Complete zero-dependency HTTP REST API framework:
  ```corvus
  get web

  set app = web.server()
  app.route("/", mk func(req) [
      givout {"status": 200, "message": "Corvus API Online"}
  ])
  app.route("/api/users", mk func(req) [
      givout {"users": {"Saatvik", "Developer"}}
  ])
  app.listen(8080)
  ```
* Supports route dispatch, query parameters, JSON serialization, and non-blocking background daemon threading.

---

### 4. 🎓 Interactive CLI Language Tour (`corvus tour`)
* In-terminal hands-on course inspired by `vimtutor` and `rustlings`.
* 8 interactive lessons with live evaluation:
  1. Hello World & `log()`
  2. Variables & Type Inference (`set`, `const`)
  3. Functions & Return Values (`mk func`, `givout`)
  4. Block Scoping `[ ... ]` & `{ ... }`
  5. Object-Oriented Classes (`cls`, `self.`)
  6. Matrix Math (`@`)
  7. Concurrency with Crows (`crow`)
  8. Structured Error Resilience (`try ... error ... final`)

---

### 5. 🔌 Language Server Protocol Daemon (`corvus lsp`)
* Full Microsoft JSON-RPC 2.0 Language Server Protocol implementation.
* Integrates with VS Code, Neovim (`nvim-lspconfig`), Sublime Text, and Helix:
  - Real-time syntax diagnostics (red error squiggles)
  - Hover documentation for all keywords, operators, and built-ins
  - Autocompletion provider for language tokens, types, and standard libraries

---

### 6. ⚡ WebAssembly (Wasm) Compilation Target (`--target wasm`)
* `corvus compile <file.crv> --target wasm [-o out.wat]`:
  - Compiles Corvus functions and statements into standard WebAssembly Text format (`.wat`).
  - Automatically generates an HTML/JavaScript browser runner for client-side execution.

---

## 🚀 Quick CLI Reference

```bash
# 1. Interactive Tour
corvus tour

# 2. Package Manager
corvus pkg init my_app
corvus pkg list

# 3. RavenAI 2.0 Suite
corvus ai testgen my_file.crv
corvus ai doc my_file.crv
corvus ai review my_file.crv
corvus ai export my_file.crv --target py

# 4. WebAssembly Export
corvus compile app.crv --target wasm

# 5. Language Server Protocol
corvus lsp
```
