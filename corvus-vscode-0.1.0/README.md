# Corvus Language Support for VS Code

Syntax highlighting, editing configuration, and snippets for the Corvus 0.1 language.

## Features

- `.crv` and `.Crv` language mode
- TextMate syntax highlighting
- Corvus `?{ ... }` block comments
- Strings and escape sequences
- Integers and floating-point numbers
- `true`, `fal`, and `null`
- Corvus keywords, declaration keywords, logical operators, and async keywords
- Corvus types
- Operators and punctuation
- Function and class declaration highlighting
- Basic built-in function highlighting
- Bracket matching and autoclosing
- Block-comment toggling
- Indentation for `[ ... ]` blocks
- Starter snippets

## Install locally

1. Open this folder in VS Code.
2. Press `F5`.
3. A new **Extension Development Host** window opens.
4. Open `examples/test.crv`.
5. The language mode should show **Corvus**.

You can also package the extension with `vsce package` after installing the VS Code Extension Manager (`vsce`).

## Scope

This first extension provides editor-side lexical highlighting. It does not replace the Corvus interpreter or `lexercorvus.py`.

## Source basis

The grammar follows the Corvus 0.1 V3 specification: `set`, `const`, `mk`, `tup`, `func`, `lmb`, `givout`, `if`, `elsif`, `else`, `for`, `in`, `while`, `brk`, `con`, `try`, `error`, `final`, `true`, `fal`, `null`, `and`, `or`, `not`, `xor`, `async`, `awt`, `cls`, `global`, `pass`, and `get`; explicit `[ ... ]` blocks; and `?{ ... }` comments.
