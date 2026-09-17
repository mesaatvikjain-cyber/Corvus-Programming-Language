# 🛠️ Corvus Automated Installation Guide (Windows, Linux, macOS)

Corvus provides automated, self-contained cross-platform installers for **every single version release** (v1.1 through v5.1) as well as **zero-dependency standalone native binaries**.

---

## 🌟 Zero-Dependency Standalone Native Binaries (No Python Required!)

If you want to run Corvus without installing Python or any build tools:

### Windows Standalone (Single-File .exe)
```powershell
# Install v5.1 (Latest: Omni-Platform Ecosystem, JIT, WebSockets, Channels, GameKit, ORM, DataFrames)
.\Distributions\Version_5.1\install_standalone_windows.ps1

# Or install v5.0
.\Distributions\Version_5.0\install_standalone_windows.ps1
```
Installs `corvus.exe` and `corvusc.exe` into your User PATH.

### Linux Standalone
```bash
# Install v5.1
bash Distributions/Version_5.1/install_standalone_linux.sh

# Or install v5.0
bash Distributions/Version_5.0/install_standalone_linux.sh
```

### macOS Standalone
```bash
# Install v5.1
bash Distributions/Version_5.1/install_standalone_macos.sh

# Or install v5.0
bash Distributions/Version_5.0/install_standalone_macos.sh
```

---

## 🪟 Windows Installation (`install_windows.ps1`)

### Master Interactive Installer (Select any Version)
Open PowerShell in the repository root and run:
```powershell
.\install_windows.ps1
```
This presents an interactive menu where you can choose:
* **`[0] Standalone Native Binaries v5.1 (Zero Python Required) [RECOMMENDED]`**
* **`[1] Version 5.1 (Omni-Platform: JIT, WebSockets, Channels, GameKit, ORM, DataFrames) [DEFAULT]`**
* **`[2] Version 5.0 (Enterprise Ecosystem: RavenAI 2.0, CPM, Web, Tour, LSP, Wasm)`**
* **`[3] Version 4.7 (RavenAI Assistant, Transpiler, Hardened VM)`**
* **`[4] Version 4.6 (Security Hardened, Bytecode VM & Fuzz Tested)`**
* **`[5] Version 4.5 (Corvus Bytecode VM & .crvc Compiler)`**
* **`[6] Version 4.4 (Universal Dual Syntax & Smart Type Inference)`**
* **`[7] - [14] Earlier Version Releases (v4.3 down to v1.1)`**

### Version-Specific Direct Installers
To install a specific version directly and register CLI wrappers (`corvus`, `corvusc`) in your user PATH:
```powershell
# Install Version 5.1 (Latest: Omni-Platform Ecosystem)
.\versions\Version_5.1\install_windows.ps1

# Install Version 5.0 (Enterprise Ecosystem)
.\versions\Version_5.0\install_windows.ps1

# Install Version 4.7 (RavenAI Assistant, Transpiler, Hardened VM)
.\versions\Version_4.7\install_windows.ps1

# Install Version 4.6 (Security Hardened & Bytecode VM)
.\versions\Version_4.6\install_windows.ps1
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
# Install Version 5.1 (Latest: Omni-Platform Ecosystem)
bash versions/Version_5.1/install_linux.sh

# Install Version 5.0 (Enterprise Ecosystem)
bash versions/Version_5.0/install_linux.sh

# Install Version 4.7
bash versions/Version_4.7/install_linux.sh

# Install Version 4.6
bash versions/Version_4.6/install_linux.sh

# Install Version 4.5
bash versions/Version_4.5/install_linux.sh
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
# Install Version 5.1 (Latest: Omni-Platform Ecosystem)
bash versions/Version_5.1/install_macos.sh

# Install Version 5.0 (Enterprise Ecosystem)
bash versions/Version_5.0/install_macos.sh

# Install Version 4.7
bash versions/Version_4.7/install_macos.sh

# Install Version 4.6
bash versions/Version_4.6/install_macos.sh

# Install Version 4.5
bash versions/Version_4.5/install_macos.sh
```
