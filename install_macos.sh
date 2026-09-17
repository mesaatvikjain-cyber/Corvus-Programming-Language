#!/bin/bash
# Corvus Master macOS Installer (Multi-Version Selector)

echo "=========================================================="
echo "   Corvus Programming Language Master macOS Installer     "
echo "=========================================================="

echo ""
echo "Select Corvus Installation Package:"
echo "  [0] Standalone Native Binaries v5.3 (Zero Python Required) [RECOMMENDED]"
echo "  [1] Version 5.3 (Cognitive Intelligence: BPE Tokenizer, Grammar Constraint & Compiler Self-Healing) [DEFAULT]"
echo "  [2] Version 5.2 (Neural AI Ecosystem: RavenLM Transformer, Code Completion & Fine-Tuning)"
echo "  [3] Version 5.1 (Omni-Platform: JIT Engine, WebSockets, Channels, GameKit, ORM, DataFrames)"
echo "  [4] Version 5.0 (Enterprise Ecosystem: RavenAI 2.0, CPM, Web, Tour, LSP, Wasm)"
echo "  [5] Version 4.7 (RavenAI Assistant, Transpiler & Hardened VM)"
echo "  [6] Version 4.6 (Security Hardened, Bytecode VM & .crvc Compiler)"
echo "  [7] Version 4.5 (Corvus Bytecode VM & .crvc Compiler)"
echo "  [8] Version 4.4 (Universal Dual Syntax & Smart Type Inference)"
echo "  [9] Version 4.3 (Latest Features & Diagnostics)"
echo " [10] Version 4.2 (Desktop 2D Graphics & Concurrency)"
echo " [11] Version 4.1 (Super Optimizer Engine)"
echo " [12] Version 4.0 (Native StdLib Expansion & REPL)"
echo " [13] Version 3.1 (Enterprise Error Resilience)"
echo " [14] Version 3.0 (Self-Hosted Compiler & Concurrency)"
echo " [15] Version 2.0 (Multi-Platform Native Assembly)"
echo " [16] Version 1.1 (AST Visitor Interpreter)"

read -p "Enter selection (0-16) [Default: 1]: " CHOICE
CHOICE=${CHOICE:-1}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if [ "$CHOICE" == "0" ]; then
    STANDALONE_INSTALLER="$SCRIPT_DIR/Distributions/Version_5.3/install_standalone_macos.sh"
    if [ ! -f "$STANDALONE_INSTALLER" ]; then
        STANDALONE_INSTALLER="$SCRIPT_DIR/Distributions/Version_5.2/install_standalone_macos.sh"
    fi
    if [ ! -f "$STANDALONE_INSTALLER" ]; then
        STANDALONE_INSTALLER="$SCRIPT_DIR/Distributions/Version_5.1/install_standalone_macos.sh"
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
    1) VER_FOLDER="Version_5.3" ;;
    2) VER_FOLDER="Version_5.2" ;;
    3) VER_FOLDER="Version_5.1" ;;
    4) VER_FOLDER="Version_5.0" ;;
    5) VER_FOLDER="Version_4.7" ;;
    6) VER_FOLDER="Version_4.6" ;;
    7) VER_FOLDER="Version_4.5" ;;
    8) VER_FOLDER="Version_4.4" ;;
    9) VER_FOLDER="Version_4.3" ;;
    10) VER_FOLDER="Version_4.2" ;;
    11) VER_FOLDER="Version_4.1" ;;
    12) VER_FOLDER="Version_4.0" ;;
    13) VER_FOLDER="Version_3.1" ;;
    14) VER_FOLDER="Version_3.0" ;;
    15) VER_FOLDER="Version_2.0" ;;
    16) VER_FOLDER="Version_1.1" ;;
    *) VER_FOLDER="Version_5.3" ;;
esac

TARGET_INSTALLER="$SCRIPT_DIR/versions/$VER_FOLDER/install_macos.sh"

if [ -f "$TARGET_INSTALLER" ]; then
    echo "[EXECUTING] Launching installer for $VER_FOLDER..."
    bash "$TARGET_INSTALLER"
else
    echo "[ERROR] Installer script not found at $TARGET_INSTALLER"
    exit 1
fi
