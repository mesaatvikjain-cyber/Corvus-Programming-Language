import sys
import os
import argparse

# Unified Multi-Platform Corvus Compiler Entry Point Driver
try:
    from Compiler_Windows.CorvusC_win64 import compile_windows
    from Compiler_Linux.CorvusC_linux import compile_linux
    from Compiler_MacOS.CorvusC_macos import compile_macos
except ImportError:
    # Ensure local sys.path resolution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Compiler_Windows.CorvusC_win64 import compile_windows
    from Compiler_Linux.CorvusC_linux import compile_linux
    from Compiler_MacOS.CorvusC_macos import compile_macos


def detect_target():
    if sys.platform.startswith("win"):
        return "windows"
    elif sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform == "darwin":
        return "macos"
    return "windows"


def main():
    parser = argparse.ArgumentParser(description="Corvus Cross-Platform Native Assembly Compiler CLI (v2.0)")
    parser.add_argument("source", help="Path to the .crv source file")
    parser.add_argument("-o", "--output", help="Custom executable name (e.g. app.exe or app)")
    parser.add_argument("-r", "--run", action="store_true", help="Run executable after compiling")
    parser.add_argument("--keep-asm", action="store_true", help="Keep intermediate .asm file")
    parser.add_argument("-t", "--target", choices=["windows", "linux", "macos"], default=detect_target(),
                        help=f"Target OS platform (default: {detect_target()})")

    args = parser.parse_args()
    source_path = args.source

    if not os.path.exists(source_path):
        print(f"[ERROR] File '{source_path}' not found.")
        sys.exit(1)

    print("======================================================")
    print("Corvus Multi-Platform Compiler v2.0")
    print("Copyright (c) 2026 Saatvik Jain. All rights reserved.")
    print(f"Target OS: {args.target.upper()}")
    print("======================================================\n")

    if args.target == "windows":
        compile_windows(source_path=source_path, output_path=args.output, run_after=args.run, keep_asm=args.keep_asm)
    elif args.target == "linux":
        compile_linux(source_path=source_path, output_path=args.output, run_after=args.run, keep_asm=args.keep_asm)
    elif args.target == "macos":
        compile_macos(source_path=source_path, output_path=args.output, run_after=args.run, keep_asm=args.keep_asm)


if __name__ == "__main__":
    main()