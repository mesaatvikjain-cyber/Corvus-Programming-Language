# 🛠️ Corvus Automated Installation Guide (Windows, Linux, macOS)

Corvus provides automated, self-contained cross-platform installers for **every single version release** (v1.1, v2.0, v3.0, v3.1, v4.0, v4.1, v4.2, v4.3, v4.4, and v4.5) as well as **zero-dependency standalone native binaries**.

---

## 🌟 Zero-Dependency Standalone Native Binaries (No Python Required!)

If you want to run Corvus without installing Python or any build tools:

### Windows Standalone (Single-File .exe)
```powershell
# Install v4.5 (Latest: CorvusVM & .crvc Compiler)
.\Distributions\Version_4.5\install_standalone_windows.ps1

# Or install v4.4
.\Distributions\Version_4.4\install_standalone_windows.ps1
```
Installs `corvus.exe` and `corvusc.exe` into your User PATH.

### Linux Standalone
```bash
# Install v4.5
bash Distributions/Version_4.5/install_standalone_linux.sh

# Or install v4.4
bash Distributions/Version_4.4/install_standalone_linux.sh
```

### macOS Standalone
```bash
# Install v4.5
bash Distributions/Version_4.5/install_standalone_macos.sh

# Or install v4.4
bash Distributions/Version_4.4/install_standalone_macos.sh
```

---

## 🪟 Windows Installation (`install_windows.ps1`)

### Master Interactive Installer (Select any Version)
Open PowerShell in the repository root and run:
```powershell
.\install_windows.ps1
```
This presents an interactive menu where you can choose:
* **`[0] Standalone Native Binaries v4.5 (Zero Python Required) [RECOMMENDED]`**
* **`[1] Version 4.5 (Corvus Bytecode VM & .crvc Compiler) [DEFAULT]`**
* **`[2] Version 4.4 (Universal Dual Syntax & Smart Type Inference)`**
* **`[3] - [10] Earlier Version Releases (v4.3 down to v1.1)`**

### Version-Specific Direct Installers
To install a specific version directly and register CLI wrappers (`corvus`, `corvusc`) in your user PATH:
```powershell
# Install Version 4.5 (Latest: Bytecode VM, .crvc Compiler & Disassembler)
.\versions\Version_4.5\install_windows.ps1

# Install Version 4.4 (Modern Ergonomics, Dual Brackets & Inference)
.\versions\Version_4.4\install_windows.ps1

# Install Version 4.3 (AI/ML Suite, Parity & Diagnostics)
.\versions\Version_4.3\install_windows.ps1
```

---

## 🐧 Linux Installation (`install_linux.sh`)

### Master Interactive Installer
Open terminal in the repository root and run:
```bash
bash install_linux.sh
```

### Version-Specific Direct Installers
```bash
# Install Version 4.5 (Latest)
bash versions/Version_4.5/install_linux.sh

# Install Version 4.4
bash versions/Version_4.4/install_linux.sh

# Install Version 4.3
bash versions/Version_4.3/install_linux.sh
```

---

## 🍏 macOS Installation (`install_macos.sh`)

### Master Interactive Installer
Open terminal in the repository root and run:
```bash
bash install_macos.sh
```

### Version-Specific Direct Installers
```bash
# Install Version 4.5 (Latest)
bash versions/Version_4.5/install_macos.sh

# Install Version 4.4
bash versions/Version_4.4/install_macos.sh

# Install Version 4.3
bash versions/Version_4.3/install_macos.sh
```
