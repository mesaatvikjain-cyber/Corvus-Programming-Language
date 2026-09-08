<p align="center">
  <img src="Documentation/corvus_logo.png" alt="Corvus Programming Language Logo" width="240"/>
</p>

<h1 align="center">Corvus Programming Language</h1>

<p align="center">
  <b>A modern, clean, and general-purpose programming language built in Python — featuring explicit block scoping, static type annotations, first-class lambdas, OOP, and friendly diagnostic errors.</b>
</p>

<p align="center">
  <a href="#-the-story-behind-corvus">The Story</a> •
  <a href="#-key-features">Key Features</a> •
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-code-showcase">Code Examples</a> •
  <a href="#-license">License</a>
</p>

---

## 📖 The Story Behind Corvus

> *"I got inspired to build my own programming language after watching a video about a programmer who created G# and C#. Since I already knew Python, I decided to take on the challenge and build my very own programming language from scratch!"*  
> — **Saatvik Jain** (11-Year-Old Creator of Corvus)

**Corvus** was born out of curiosity and a passion for computer science. Instead of relying on indentation (like Python) or curly braces (like C/JavaScript), Corvus introduces a unique syntax using square brackets `[ ... ]` for code blocks, reserving curly braces `{ ... }` for native lists. It combines the ease of Python with explicit type declarations, structured error recovery, and actionable developer diagnostics.

---

## 🌟 Key Features

* **📦 Explicit Scope Delimiters**: Code blocks use brackets `[ ... ]` for clean, unambiguous scope boundaries.
* **🏷️ Explicit Type Declarations**: `set <type>; name = value` for typed variables and `set const; NAME = value` for immutable constants.
* **🎯 Actionable Error Diagnostics**: Custom diagnostic engine that points to the exact line/column with caret pointers (`^`) and actionable fix suggestions.
* **⚡ First-Class Lambdas**: Inline and block lambdas (`lmb[x] => x * 2`) with functional list transformations (`.map()`, `.filter()`).
* **🧬 Object-Oriented Programming**: Complete support for classes (`cls Person() [ ... ]`) with `init` constructors and `self` instance dispatch.
* **🛡️ Structured Exception Recovery**: `try [ ... ] error(e) [ ... ] final [ ... ]` blocks.
* **📚 Native Standard Modules**: Built-in modules including `get math` (`math.pi`, `math.sqrt`) and `get system`.

---

## 🚀 Quickstart

### Prerequisites
Make sure you have **Python 3.8+** installed on your computer.

### Running a Corvus Script
Clone the repository and run any `.crv` file using the Corvus driver:

```bash
git clone https://github.com/YOUR_USERNAME/Corvus.git
cd Corvus
python Corvus.py test_v01.crv
```

---

## 💻 Code Showcase

### 1. Factorial Recursion & Control Flow
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

### 2. Lambdas & Higher-Order List Operations
```corvus
set lis; numbers = {1, 2, 3, 4, 5}
set lmb; double_fn = lmb[x] => x * 2

set lis; doubled_list = numbers.map(double_fn)
log("Doubled numbers:", doubled_list)
```

### 3. Object-Oriented Class Declaration
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

set Person; user = Person("Saatvik Jain", 22)
user.describe()
```

### 4. Diagnostic Error Handling
```corvus
try [
    log("Executing calculation...")
    set int; result = 10 / 0
] error(err) [
    log("Caught error safely ->", err["message"])
] final [
    log("Cleanup block executed.")
]
```

---

## 🏗️ Architecture & How It Works

Corvus is built using a textbook 5-stage compiler pipeline:

$$\text{Corvus Source Code (.crv)} \xrightarrow{\text{Lexer}} \text{Tokens} \xrightarrow{\text{Parser}} \text{AST} \xrightarrow{\text{Evaluator + Environment}} \text{Execution}$$

1. **Lexer** ([`lexercorvus.py`](lexercorvus.py)): Tokenizes source code into typed tokens while handling comments (`?{ ... }`) and multi-line offsets.
2. **Parser** ([`parsercorvus.py`](parsercorvus.py)): Recursive-descent parser constructing Abstract Syntax Tree (AST) nodes with an operator precedence ladder.
3. **AST** ([`astnodes.py`](astnodes.py)): Strongly-typed dataclass representation of all language primitives.
4. **Evaluator** ([`evaluatorcorvus.py`](evaluatorcorvus.py)): AST Visitor interpreter managing lexically-scoped `Environment` trees and runtime dispatch.
5. **Diagnostics** ([`errors.py`](errors.py)): Formatted exception formatter printing precise line/column pointers and fix suggestions.

---

## 📄 License & Author

* **Author**: Saatvik Jain (11-Year-Old Developer)
* **Documentation**: See [`Corvus v0.1.0.docx`](Corvus%20v0.1.0.docx) for the full language reference specification.
* **License**: Released under the open-source [MIT License](LICENSE).
