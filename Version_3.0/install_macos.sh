#!/bin/bash
# Corvus v3.0 Automated macOS Installer

echo "================================================"
echo "   Installing Corvus Programming Language v3.0  "
echo "================================================"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

cat <<EOF > "$BIN_DIR/corvus-v3.0"
#!/bin/bash
python3 "$SCRIPT_DIR/Interpreter/Corvus.py" "\$@"
EOF

cat <<EOF > "$BIN_DIR/corvusc-v3.0"
#!/bin/bash
python3 "$SCRIPT_DIR/Compiler_MacOS/CorvusC_macos.py" "\$@"
EOF

chmod +x "$BIN_DIR/corvus-v3.0" "$BIN_DIR/corvusc-v3.0"
echo "[SUCCESS] Installed Corvus v3.0 wrappers to '$BIN_DIR'"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
fi

echo "[INSTALL COMPLETE] Run: corvus-v3.0 <file.crv> or corvusc-v3.0 <file.crv>"
