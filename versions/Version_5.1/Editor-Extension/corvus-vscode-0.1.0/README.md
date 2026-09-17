# Corvus Language Support for VS Code (v0.2.0)

Rich syntax highlighting, language configuration, code folding, and snippets for the Corvus programming language.

## Features

- `.crv` and `.Crv` language mode
- TextMate syntax highlighting for Corvus v2.0
- **Comments**: `//` single-line, `#` single-line, and `?{ ... }` block comments with Ctrl+/ toggle support
- **Operators**: Pipeline operator `|>`, Fat arrow `=>`, Safe navigation `?.`, Null coalescing `??`, and logical `and`/`or`/`not`/`xor`
- **Pattern Matching**: `match`, `case`, `else` syntax highlighting and automatic block indentation
- **Strings & Escapes**: Double-quoted `"..."` and single-quoted `'...'` strings with full escape sequence highlighting
- **Numbers**: Integer and floating-point literals
- **Keywords & Types**: All Corvus keywords (`set`, `const`, `mk`, `func`, `lmb`, `cls`, `givout`, `if`, `elsif`, `else`, `for`, `in`, `while`, `brk`, `con`, `try`, `error`, `final`, `pass`, `global`, `get`, `input`, `async`, `awt`) and primitive storage types (`int`, `flo`, `str`, `bool`, `lis`, `tup`, `dic`, `func`, `lmb`)
- **Constants**: `true`, `fal`, `null`, `self`
- **Built-in Functions**: Highlighting for `log`, `type`, `range`, `sum`, `min`, `max`, `abs`, `round`, `any`, `all`, `reversed`, `sorted`, `enumerate`, `input`
- **Standard Modules**: Highlighting for `gui`, `http`, `process`, `math`, `system`, `random`, `time`, `file`, `json`, `os`, `sys`, `urllib`
- **Editing & Code Folding**: Explicit `[ ... ]` code block folding, autoclosing pairs, surrounding pairs, and intelligent indentation
- **18+ Rich Snippets**: Complete snippet library for functions, async functions, classes, pattern matching, pipelines, loops, try/error/final, GUI alerts, HTTP requests, and native user input

## Installation

### From VSIX Package
1. Open VS Code.
2. Go to **Extensions** (`Ctrl+Shift+X`).
3. Click the `...` menu at the top right of the Extensions panel.
4. Select **Install from VSIX...**
5. Select `corvus-language-support-0.2.0.vsix` located in `Editor-Extension/`.

### Local Extension Development
1. Open `Editor-Extension/corvus-vscode-0.1.0` in VS Code.
2. Press `F5` to open the **Extension Development Host**.
3. Open any `.crv` file to test full language support!

