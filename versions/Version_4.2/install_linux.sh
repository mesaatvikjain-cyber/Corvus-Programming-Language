#!/bin/bash
# Corvus v4.2 Automated Linux Installer

echo "================================================"
echo "   Installing Corvus Programming Language v4.2  "
echo "================================================"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

cat <<EOF > "$BIN_DIR/corvus-v4.2"
#!/bin/bash
python3 "$SCRIPT_DIR/Interpreter/Corvus.py" "\$@"
EOF

cat <<EOF > "$BIN_DIR/corvusc-v4.2"
#!/bin/bash
python3 "$SCRIPT_DIR/Compiler_Linux/CorvusC_linux.py" "\$@"
EOF

chmod +x "$BIN_DIR/corvus-v4.2" "$BIN_DIR/corvusc-v4.2"
echo "[SUCCESS] Installed Corvus v4.2 wrappers to '$BIN_DIR'"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi

echo "[INSTALL COMPLETE] Run: corvus-v4.2 <file.crv> or corvusc-v4.2 <file.crv>"
