# 🛠️ Corvus Automated Installation Guide (Windows, Linux, macOS)

Corvus provides automated, self-contained cross-platform installers for **every single version release** (1.1, 2.0, 3.0, 3.1, 4.0, 4.1, 4.2, 4.3) as well as interactive master installers.

---

## 🪟 Windows Installation (install_windows.ps1)

### Master Interactive Installer (Select any Version)
Open PowerShell in the repository root and run:
`powershell
.\install_windows.ps1
`
This presents an interactive menu to choose between **v1.1**, **v2.0**, **v3.0**, **v3.1**, **v4.0**, **v4.1**, **v4.2**, or **v4.3 [DEFAULT]**.

### Version-Specific Direct Installers
To install a specific version directly and register CLI wrappers (corvus, corvusc) in your user PATH:
`powershell
# Install Version 4.3 (Latest: AI/ML Suite, Parity & Diagnostics)
.\Version_4.3\install_windows.ps1

# Install Version 4.2 (Desktop 2D Graphics & Concurrency)
.\Version_4.2\install_windows.ps1

# Install Version 4.1 (Super Optimization Engine)
.\Version_4.1\install_windows.ps1

# Install Version 4.0 (Native StdLib & REPL)
.\Version_4.0\install_windows.ps1
`

---

## 🐧 Linux Installation (install_linux.sh)

### Master Interactive Installer
Open terminal in the repository root and run:
`ash
bash install_linux.sh
`

### Version-Specific Direct Installers
`ash
# Install Version 4.3 (Latest)
bash Version_4.3/install_linux.sh

# Install Version 4.2
bash Version_4.2/install_linux.sh

# Install Version 4.1
bash Version_4.1/install_linux.sh
`

---

## 🍏 macOS Installation (install_macos.sh)

### Master Interactive Installer
Open terminal in the repository root and run:
`ash
bash install_macos.sh
`

### Version-Specific Direct Installers
`ash
# Install Version 4.3 (Latest)
bash Version_4.3/install_macos.sh

# Install Version 4.2
bash Version_4.2/install_macos.sh

# Install Version 4.1
bash Version_4.1/install_macos.sh
`
