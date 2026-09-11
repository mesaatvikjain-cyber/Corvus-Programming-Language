---
name: Bug Report
about: Create a report to help improve Corvus
title: '[BUG] <Short Description>'
labels: 'bug'
assignees: ''

---

## 🐛 Bug Description
A clear and concise description of what the bug is.

## 💻 Environment
- **Corvus Version**: (e.g. v4.6, v4.5, v4.4, or commit hash)
- **Operating System**: (e.g. Windows 11, Ubuntu 24.04, macOS Sonoma)
- **Architecture**: (e.g. x86_64, ARM64)
- **Execution Mode**: (e.g. AST Interpreter, Bytecode VM (`--vm`), or Native C99 Compiler (`corvusc`))

## 📝 Reproducing .crv Program
Please provide a minimal, self-contained `.crv` code snippet that reproduces the issue:

```corvus
// Paste your minimal reproducible .crv code here
func main() [
    // ...
]
```

## 🔄 Command Executed
```bash
corvus myfile.crv
# or
corvus --vm myfile.crv
# or
corvusc myfile.crv -o myfile.exe --run
```

## 🎯 Expected Behavior
A clear and concise description of what you expected to happen.

## 💥 Actual Behavior & Error Output
```text
// Paste the full terminal output, traceback, or compiler error message here
```

## 🔍 Additional Context
Add any other context, standard library modules involved (`get <module>`), or diagnostic logs here.
