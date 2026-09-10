#!/bin/bash
# Corvus Master Linux Installer (Multi-Version Selector)

echo "=========================================================="
echo "   Corvus Programming Language Master Linux Installer     "
echo "=========================================================="

echo ""
echo "Select Corvus Installation Package:"
echo "  [0] Standalone Native Binaries v4.4 (Zero Python Required) [RECOMMENDED]"
echo "  [1] Version 4.4 (Universal Dual Syntax & Smart Type Inference) [DEFAULT]"
echo "  [2] Version 4.3 (Latest Features & Diagnostics)"
echo "  [3] Version 4.2 (Desktop 2D Graphics & Concurrency)"
echo "  [4] Version 4.1 (Super Optimizer Engine)"
echo "  [5] Version 4.0 (Native StdLib Expansion & REPL)"
echo "  [6] Version 3.1 (Enterprise Error Resilience)"
echo "  [7] Version 3.0 (Self-Hosted Compiler & Concurrency)"
echo "  [8] Version 2.0 (Multi-Platform Native Assembly)"
echo "  [9] Version 1.1 (AST Visitor Interpreter)"

read -p "Enter selection (0-9) [Default: 0]: " CHOICE
CHOICE=${CHOICE:-0}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if [ "$CHOICE" == "0" ]; then
    STANDALONE_INSTALLER="$SCRIPT_DIR/Distributions/Version_4.4/install_standalone_linux.sh"
    if [ -f "$STANDALONE_INSTALLER" ]; then
        echo "[EXECUTING] Launching Standalone Native Binaries Installer..."
        bash "$STANDALONE_INSTALLER"
        exit 0
    fi
fi

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 is required for source installations but was not found."
    echo "Tip: Choose option [0] to install Standalone Native Binaries with zero Python required!"
    exit 1
fi

case $CHOICE in
    1) VER_FOLDER="Version_4.4" ;;
    2) VER_FOLDER="Version_4.3" ;;
    3) VER_FOLDER="Version_4.2" ;;
    4) VER_FOLDER="Version_4.1" ;;
    5) VER_FOLDER="Version_4.0" ;;
    6) VER_FOLDER="Version_3.1" ;;
    7) VER_FOLDER="Version_3.0" ;;
    8) VER_FOLDER="Version_2.0" ;;
    9) VER_FOLDER="Version_1.1" ;;
    *) VER_FOLDER="Version_4.4" ;;
esac

TARGET_INSTALLER="$SCRIPT_DIR/$VER_FOLDER/install_linux.sh"

if [ -f "$TARGET_INSTALLER" ]; then
    echo "[EXECUTING] Launching installer for $VER_FOLDER..."
    bash "$TARGET_INSTALLER"
else
    echo "[ERROR] Installer script not found at $TARGET_INSTALLER"
    exit 1
fi
