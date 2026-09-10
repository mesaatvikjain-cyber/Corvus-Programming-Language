#!/bin/bash
# Corvus v1.1 Automated Linux Installer

echo "================================================"
echo "   Installing Corvus Programming Language v1.1  "
echo "================================================"

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.8+."
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

CORVUS_WRAPPER="$BIN_DIR/corvus-v1.1"

cat <<EOF > "$CORVUS_WRAPPER"
#!/bin/bash
python3 "$SCRIPT_DIR/Interpreter/Corvus.py" "\$@"
EOF

chmod +x "$CORVUS_WRAPPER"
echo "[SUCCESS] Installed Corvus v1.1 wrapper to '$CORVUS_WRAPPER'"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo "[INFO] Added $BIN_DIR to ~/.bashrc"
fi

echo "[INSTALL COMPLETE] Corvus v1.1 installed! Run with: corvus-v1.1 <file.crv>"
