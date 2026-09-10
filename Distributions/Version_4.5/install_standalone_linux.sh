#!/usr/bin/env bash
# install_standalone_linux.sh
# One-click Linux installer for Corvus v4.4 Standalone Native Binaries

echo "============================================================"
echo "  Corvus v4.4 Standalone Native Binaries Installer (Linux)  "
echo "============================================================"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
STANDALONE_DIR="$SCRIPT_DIR/standalone"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$BIN_DIR"

if [ -f "$STANDALONE_DIR/corvus" ]; then
    cp "$STANDALONE_DIR/corvus" "$BIN_DIR/corvus"
    cp "$STANDALONE_DIR/corvusc" "$BIN_DIR/corvusc"
    chmod +x "$BIN_DIR/corvus" "$BIN_DIR/corvusc"
    echo "[SUCCESS] Installed standalone binaries to $BIN_DIR"
else
    # Fallback: create symlink wrappers to portable SDK launcher
    ln -sf "$SCRIPT_DIR/portable-sdk/bin/corvus" "$BIN_DIR/corvus"
    ln -sf "$SCRIPT_DIR/portable-sdk/bin/corvusc" "$BIN_DIR/corvusc"
    chmod +x "$BIN_DIR/corvus" "$BIN_DIR/corvusc"
    echo "[SUCCESS] Linked portable SDK launchers to $BIN_DIR"
fi

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$HOME/.bashrc"
    echo "[INFO] Added '$BIN_DIR' to ~/.bashrc"
fi

echo ""
echo "[INSTALL COMPLETE] Run: corvus <file.crv> or corvusc <file.crv>"
