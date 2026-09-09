# 🛠️ Corvus Automated Installation Guide (Windows, Linux, macOS)

Corvus provides automated, self-contained cross-platform installers for **every single version release** (`v1.1`, `v2.0`, `v3.0`, `v3.1`, `v4.0`, `v4.1`) as well as interactive master installers.

---

## 🪟 Windows Installation (`install_windows.ps1`)

### Master Interactive Installer (Select any Version)
Open PowerShell and run:
```powershell
.\install_windows.ps1
```

### Version-Specific Direct Installers
To install a specific version directly:
```powershell
# Install Version 4.1 (Latest)
.\Version_4.1\install_windows.ps1

# Install Version 4.0
.\Version_4.0\install_windows.ps1

# Install Version 3.1
.\Version_3.1\install_windows.ps1
```

---

## 🐧 Linux Installation (`install_linux.sh`)

### Master Interactive Installer
Open terminal and run:
```bash
bash install_linux.sh
```

### Version-Specific Direct Installers
```bash
# Install Version 4.1 (Latest)
bash Version_4.1/install_linux.sh

# Install Version 4.0
bash Version_4.0/install_linux.sh
```

---

## 🍏 macOS Installation (`install_macos.sh`)

### Master Interactive Installer
Open terminal and run:
```bash
bash install_macos.sh
```

### Version-Specific Direct Installers
```bash
# Install Version 4.1 (Latest)
bash Version_4.1/install_macos.sh

# Install Version 4.0
bash Version_4.0/install_macos.sh
```
