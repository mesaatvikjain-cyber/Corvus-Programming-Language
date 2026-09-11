#!/usr/bin/env bash
# install_standalone_macos.sh
# One-click macOS installer for Corvus v4.6 Standalone Native Binaries

echo "============================================================"
echo "  Corvus v4.6 Standalone Native Binaries Installer (macOS)  "
echo "============================================================"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
STANDALONE_DIR="$SCRIPT_DIR/standalone"
BIN_DIR="/usr/local/bin"

if [ ! -w "$BIN_DIR" ]; then
    BIN_DIR="$HOME/.local/bin"
    mkdir -p "$BIN_DIR"
fi

if [ -f "$STANDALONE_DIR/corvus" ]; then
    cp "$STANDALONE_DIR/corvus" "$BIN_DIR/corvus"
    cp "$STANDALONE_DIR/corvusc" "$BIN_DIR/corvusc"
    chmod +x "$BIN_DIR/corvus" "$BIN_DIR/corvusc"
    echo "[SUCCESS] Installed standalone binaries to $BIN_DIR"
else
    ln -sf "$SCRIPT_DIR/portable-sdk/bin/corvus" "$BIN_DIR/corvus"
    ln -sf "$SCRIPT_DIR/portable-sdk/bin/corvusc" "$BIN_DIR/corvusc"
    chmod +x "$BIN_DIR/corvus" "$BIN_DIR/corvusc"
    echo "[SUCCESS] Linked portable SDK launchers to $BIN_DIR"
fi

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    PROFILE="$HOME/.zshrc"
    [ -f "$HOME/.bash_profile" ] && PROFILE="$HOME/.bash_profile"
    echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$PROFILE"
    echo "[INFO] Added '$BIN_DIR' to $PROFILE"
fi

echo ""
echo "[INSTALL COMPLETE] Run: corvus <file.crv> or corvusc <file.crv>"
