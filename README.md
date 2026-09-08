<p align="center">
  <img src="Documentation/corvus_logo.png" alt="Corvus Programming Language Logo" width="240"/>
</p>

<h1 align="center">Corvus Programming Language (v2.0)</h1>

<p align="center">
  <b>A modern, clean, general-purpose programming language featuring explicit block scoping <code>[ ... ]</code>, static type annotations, first-class lambdas, OOP, native input, an AST Interpreter, and a 64-bit x86 Native Assembly Compiler.</b>
</p>

<p align="center">
  <a href="#-the-story-behind-corvus">The Story</a> •
  <a href="#-key-features">Key Features</a> •
  <a href="#-architecture--dual-engine">Architecture</a> •
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-code-showcase">Code Showcase</a> •
  <a href="#-license--author">License</a>
</p>

---

## 📖 The Story Behind Corvus

> *"I got inspired to build my own programming language after watching a video about a programmer who created G# and C#, and a video by AstroSam. Since I already knew Python, I decided to take on the challenge and build my very own programming language from scratch!"*  
> — **Saatvik Jain** (Creator of Corvus)

**Corvus** was born out of curiosity and a passion for computer science. Instead of relying on indentation (like Python) or curly braces (like C/JavaScript), Corvus introduces a unique syntax using **square brackets `[ ... ]` for code blocks**, reserving **curly braces `{ ... }` for native lists**. 

It has grown from an interpreted language into a full-fledged compiled language with an automated **64-bit x86 NASM Machine Code Compiler (`CorvusC`)** that translates `.crv` source code into standalone `.exe` executables!

---

## 🌟 Key Features

* **📦 Explicit Scope Delimiters**: Code blocks use brackets `[ ... ]` for clean, unambiguous scope boundaries.
* **🏷️ Explicit Type Declarations**: `set <type>; name = value` for typed variables and `set const; NAME = value` for immutable constants.
* **⌨️ Native User Input**: `input("Prompt: ")` supported natively in both Interpreter and Compiled modes.
* **⚡ First-Class Lambdas**: Inline and block lambdas (`lmb[x] => x * 2`) with functional list transformations (`.map()`, `.filter()`).
* **🧬 Object-Oriented Programming**: Complete support for classes (`cls Person() [ ... ]`) with `init` constructors and `self` instance dispatch.
* **⚙️ 64-bit Native NASM Compiler**: Emits pure x86-64 NASM Assembly and links native `.exe` executables via `nasm` and LLVM `clang`.
* **🔗 Universal Python Module Bridge & CPM Package Manager**: Import any Python library (`get os`, `get urllib`) or install Corvus community packages with `cpm install`.
* **🎯 Actionable Error Diagnostics**: Custom diagnostic engine that points to the exact line/column with caret pointers (`^`) and fix suggestions.
* **🧰 Full Suite of Built-in Utility Functions**: Native global functions including `type()`, `range()`, `sum()`, `min()`, `max()`, `abs()`, `round()`, `any()`, `all()`, `reversed()`, `sorted()`, and `enumerate()`.
* **📚 Built-in Standard Libraries**: Native modules including `get math`, `get system`, `get random`, `get time`, `get file`, `get json`, `get gui` (`gui.alert`, `gui.prompt`), `get http` (`http.get`, `http.post`), and `get process` (`process.run`, `process.cwd`).


---

## 🏗️ Architecture & Dual Engine

Corvus operates on a textbook 5-stage pipeline with two execution backends:

$$\text{Corvus Source (.crv)} \xrightarrow{\text{Lexer}} \text{Tokens} \xrightarrow{\text{Parser}} \text{AST} \begin{cases} \xrightarrow{\text{Evaluator}} \text{Interpreted Execution} \\ \xrightarrow{\text{AsmGenerator}} \text{NASM x86-64} \xrightarrow{\text{Linker}} \text{Native .exe} \end{cases}$$

1. **Lexer** ([`Interpreter/lexercorvus.py`](Interpreter/lexercorvus.py)): Tokenizes source code into typed tokens while handling comments (`?{ ... }`, `//`, `#`).
2. **Parser** ([`Interpreter/parsercorvus.py`](Interpreter/parsercorvus.py)): Recursive-descent parser constructing Abstract Syntax Tree (AST) nodes with operator precedence.
3. **Interpreter Backend** ([`Interpreter/evaluatorcorvus.py`](Interpreter/evaluatorcorvus.py)): AST Visitor interpreter managing lexically-scoped environment trees and CPM module loading.
4. **Compiler Backend** ([`Compiler/compiler_asm.py`](Compiler/compiler_asm.py)): 64-bit x86 NASM Assembly generator supporting Win64 calling conventions and C library `printf` / `scanf` calls.
5. **Compiler Driver** ([`Compiler/CorvusC.py`](Compiler/CorvusC.py)): One-command build system with automatic toolchain discovery for `nasm` and LLVM `clang`.
6. **Package Manager (`cpm`)** ([`bin/cpm.py`](bin/cpm.py)): Official package manager for project manifest management (`corvus.json`) and dependency installation.

---

## 🚀 Quickstart

### Prerequisites
* **Python 3.8+**
* Optional for Native `.exe` Compilation:
  ```powershell
  winget install NASM.NASM
  winget install MartinStorsjo.LLVM-MinGW.UCRT
  ```

### Installation & Global CLI Setup
Clone the repository and add the `bin/` directory to your system PATH:

```bash
git clone https://github.com/mesaatvikjain-cyber/Corvus-Programming-Language-.git
cd Corvus
```

### Running Corvus Commands

#### 1. Corvus Package Manager (`cpm`)
```cmd
# Initialize a new Corvus project manifest (corvus.json)
cpm init

# Install a package from GitHub or local path
cpm install username/repository
cpm install ./local_package_folder

# Install all project dependencies
cpm install

# List installed local & global packages
cpm list
```

#### 2. Native Compiler (`corvusc`)
```cmd
# Compile and run native executable directly
corvusc Examples-and-Tests/01_hello_and_input.crv -r

# Compile to custom binary name
corvusc main.crv -o my_app.exe
```

#### 3. Interpreter (`corvus`)
```cmd
corvus Examples-and-Tests/06_cpm_package_demo.crv
```


---

## 💻 Code Showcase

### 1. Interactive Native Input & Arithmetic
```corvus
set str; name = input("Enter your name: ")
set int; age = input("Enter your age: ")

log("Hello,", name)
log("Next year you will be:", age + 1)
```

### 2. Factorial Recursion & Control Flow
```corvus
?{ Pure recursive function in Corvus }
mk func factorial(n) [
    if (n <= 1) [
        givout 1
    ]
    givout n * factorial(n - 1)
]

log("Factorial of 5 is:", factorial(5))
```

### 3. Lambdas & Higher-Order List Operations
```corvus
set lis; numbers = {1, 2, 3, 4, 5}
set lmb; double_fn = lmb[x] => x * 2

set lis; doubled_list = numbers.map(double_fn)
log("Doubled numbers:", doubled_list)
```

### 4. Object-Oriented Class Declaration
```corvus
cls Person() [
    set str; name
    set int; age

    mk func init(name_val, age_val) [
        self.name = name_val
        self.age = age_val
    ]

    mk func describe() [
        log("Person -> Name:", self.name, "| Age:", self.age)
    ]
]

set Person; user = Person("Saatvik Jain", 11)
user.describe()
```

---

## 📂 Repository Structure

```
Corvus/
├── bin/                    # Global CLI launch scripts (corvus.bat, corvusc.bat)
├── Compiler/               # 64-bit Native NASM Compiler & CorvusC CLI Driver
│   ├── compiler_asm.py     # x86-64 NASM Code Generator
│   ├── CorvusC.py          # One-Click Compiler CLI Driver
│   └── Lexercompiler.py    # Compiler Lexer
├── Interpreter/            # AST Visitor Interpreter Engine
│   ├── Corvus.py           # Interpreter CLI Driver
│   ├── evaluatorcorvus.py  # AST Evaluator & Scoping Environment
│   ├── lexercorvus.py      # Lexer
│   ├── parsercorvus.py     # Parser
│   └── errors.py           # Diagnostic Caret Error Formatter
├── Documentation/          # Official Specifications (.docx) & Logos
├── Editor-Extension/       # VS Code Syntax Highlighting Extension
└── Examples-and-Tests/     # Runnable Corvus Example Programs
```

---

## 📄 License & Author

* **Author**: Saatvik Jain (Creator of Corvus)
* **Documentation**: See [`Documentation/Corvus v0.1.0.docx`](Documentation/) for the full language reference specification.
* **License**: Released under the open-source [MIT License](LICENSE).
