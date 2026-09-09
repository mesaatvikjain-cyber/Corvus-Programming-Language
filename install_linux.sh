#!/bin/bash
# Corvus Master Linux Installer (Multi-Version Selector)

echo "=========================================================="
echo "   Corvus Programming Language Master Linux Installer     "
echo "=========================================================="

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 is required but was not found."
    exit 1
fi

echo ""
echo "Select Corvus Version to Install:"
echo "  [1] Version 4.3 (Latest Features & Diagnostics) [DEFAULT]"
echo "  [2] Version 4.2 (Desktop 2D Graphics & Concurrency)"
echo "  [3] Version 4.1 (Super Optimizer Engine)"
echo "  [4] Version 4.0 (Native StdLib Expansion & REPL)"
echo "  [5] Version 3.1 (Enterprise Error Resilience)"
echo "  [6] Version 3.0 (Self-Hosted Compiler & Concurrency)"
echo "  [7] Version 2.0 (Multi-Platform Native Assembly)"
echo "  [8] Version 1.1 (AST Visitor Interpreter)"

read -p "Enter selection (1-8) [Default: 1]: " CHOICE
CHOICE=${CHOICE:-1}

case $CHOICE in
    1) VER_FOLDER="Version_4.3" ;;
    2) VER_FOLDER="Version_4.2" ;;
    3) VER_FOLDER="Version_4.1" ;;
    4) VER_FOLDER="Version_4.0" ;;
    5) VER_FOLDER="Version_3.1" ;;
    6) VER_FOLDER="Version_3.0" ;;
    7) VER_FOLDER="Version_2.0" ;;
    8) VER_FOLDER="Version_1.1" ;;
    *) VER_FOLDER="Version_4.3" ;;
esac

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
TARGET_INSTALLER="$SCRIPT_DIR/$VER_FOLDER/install_linux.sh"

if [ -f "$TARGET_INSTALLER" ]; then
    echo "[EXECUTING] Launching installer for $VER_FOLDER..."
    bash "$TARGET_INSTALLER"
else
    echo "[ERROR] Installer script not found at $TARGET_INSTALLER"
    exit 1
fi
