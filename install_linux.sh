#!/bin/bash
# Corvus Master Linux Installer (Multi-Version Selector)

echo "=========================================================="
echo "   Corvus Programming Language Master Linux Installer     "
echo "=========================================================="

echo ""
echo "Select Corvus Installation Package:"
echo "  [0] Standalone Native Binaries v4.7 (Zero Python Required) [RECOMMENDED]"
echo "  [1] Version 4.7 (RavenAI Assistant, Transpiler & Hardened VM) [DEFAULT]"
echo "  [2] Version 4.6 (Security Hardened, Bytecode VM & .crvc Compiler)"
echo "  [3] Version 4.5 (Corvus Bytecode VM & .crvc Compiler)"
echo "  [4] Version 4.4 (Universal Dual Syntax & Smart Type Inference)"
echo "  [5] Version 4.3 (Latest Features & Diagnostics)"
echo "  [6] Version 4.2 (Desktop 2D Graphics & Concurrency)"
echo "  [7] Version 4.1 (Super Optimizer Engine)"
echo "  [8] Version 4.0 (Native StdLib Expansion & REPL)"
echo "  [9] Version 3.1 (Enterprise Error Resilience)"
echo " [10] Version 3.0 (Self-Hosted Compiler & Concurrency)"
echo " [11] Version 2.0 (Multi-Platform Native Assembly)"
echo " [12] Version 1.1 (AST Visitor Interpreter)"

read -p "Enter selection (0-12) [Default: 1]: " CHOICE
CHOICE=${CHOICE:-1}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if [ "$CHOICE" == "0" ]; then
    STANDALONE_INSTALLER="$SCRIPT_DIR/Distributions/Version_4.7/install_standalone_linux.sh"
    if [ ! -f "$STANDALONE_INSTALLER" ]; then
        STANDALONE_INSTALLER="$SCRIPT_DIR/Distributions/Version_4.6/install_standalone_linux.sh"
    fi
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
    1) VER_FOLDER="Version_4.7" ;;
    2) VER_FOLDER="Version_4.6" ;;
    3) VER_FOLDER="Version_4.5" ;;
    4) VER_FOLDER="Version_4.4" ;;
    5) VER_FOLDER="Version_4.3" ;;
    6) VER_FOLDER="Version_4.2" ;;
    7) VER_FOLDER="Version_4.1" ;;
    8) VER_FOLDER="Version_4.0" ;;
    9) VER_FOLDER="Version_3.1" ;;
    10) VER_FOLDER="Version_3.0" ;;
    11) VER_FOLDER="Version_2.0" ;;
    12) VER_FOLDER="Version_1.1" ;;
    *) VER_FOLDER="Version_4.7" ;;
esac

TARGET_INSTALLER="$SCRIPT_DIR/versions/$VER_FOLDER/install_linux.sh"

if [ -f "$TARGET_INSTALLER" ]; then
    echo "[EXECUTING] Launching installer for $VER_FOLDER..."
    bash "$TARGET_INSTALLER"
else
    echo "[ERROR] Installer script not found at $TARGET_INSTALLER"
    exit 1
fi
