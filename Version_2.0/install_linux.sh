#!/bin/bash
# Corvus v2.0 Automated Linux Installer

echo "================================================"
echo "   Installing Corvus Programming Language v2.0  "
echo "================================================"

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found."
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

cat <<EOF > "$BIN_DIR/corvus-v2.0"
#!/bin/bash
python3 "$SCRIPT_DIR/Interpreter/Corvus.py" "\$@"
EOF

cat <<EOF > "$BIN_DIR/corvusc-v2.0"
#!/bin/bash
python3 "$SCRIPT_DIR/Compiler/CorvusC.py" "\$@"
EOF

chmod +x "$BIN_DIR/corvus-v2.0" "$BIN_DIR/corvusc-v2.0"
echo "[SUCCESS] Installed Corvus v2.0 wrappers to '$BIN_DIR'"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi

echo "[INSTALL COMPLETE] Run: corvus-v2.0 <file.crv> or corvusc-v2.0 <file.crv>"
