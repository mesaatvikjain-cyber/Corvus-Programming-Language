import sys
import os
import shutil
import subprocess
import argparse

# Import your Corvus Compiler pipeline components
from Lexercompiler import tokenize
from parser import Parser
from compiler_asm import AsmGenerator
print("Corvus Compiler v0.1.0")
print("\n")
print("Copyright (c) 2026 Saatvik Jain. All rights reserved.")
print("\n")
print("Licensed under the MIT License. See LICENSE for details.")
print("\n")
print("This software is provided 'as-is', without any express or implied warranty.")
print("\n")
print("Use at your own risk. The author is not responsible for any damage or loss caused by the use of this software.")
print("\n")
print("This is the compiler for the Corvus programming language. It gives you .exe files you can run on your computer. It is not a virtual machine or an interpreter. It is a compiler that translates Corvus code into machine code that can be executed directly by your computer's CPU.")
print("\n")
print("Corvus is a statically typed, compiled programming language that is designed to be simple, fast, and safe. It is inspired by languages like C, C++, and Rust, but it has its own unique features and syntax.")
print("\n")
print("Corvus is still in development, and this compiler is a work in progress. It may have bugs, and some features may not be fully implemented yet. Please report any issues you encounter to the author.")
print("\n")
print("The command for this compiler is: python CorvusC.py <source_file.crv> -o <output_file.exe>")
def find_tool(names):
    for name in names:
        path = shutil.which(name)
        if path:
            return path

    local_app_data = os.environ.get("LOCALAPPDATA", "")
    search_dirs = [
        os.path.join(local_app_data, "bin", "NASM"),
        os.path.join(local_app_data, "Microsoft", "WinGet", "Links"),
        r"C:\msys64\mingw64\bin",
    ]

    winget_pkg_dir = os.path.join(local_app_data, "Microsoft", "WinGet", "Packages")
    if os.path.exists(winget_pkg_dir):
        for entry in os.listdir(winget_pkg_dir):
            if "LLVM-MinGW" in entry:
                pkg_path = os.path.join(winget_pkg_dir, entry)
                for root, dirs, files in os.walk(pkg_path):
                    if os.path.basename(root).lower() == "bin":
                        search_dirs.insert(0, root)


    for d in search_dirs:
        for name in names:
            full = os.path.join(d, name if name.endswith(".exe") else f"{name}.exe")
            if os.path.exists(full):
                return full
    return None


def main():
    parser = argparse.ArgumentParser(description="Corvus Native Assembly Compiler CLI")
    parser.add_argument("source", help="Path to the .crv source file")
    parser.add_argument("-o", "--output", help="Custom executable name (e.g. output.exe)")
    parser.add_argument("-r", "--run", action="store_true", help="Run executable after compiling")
    parser.add_argument("--keep-asm", action="store_true", help="Keep intermediate .asm file")

    args = parser.parse_args()
    source_path = args.source
    if not os.path.exists(source_path):
        print(f"[ERROR] File '{source_path}' not found.")
        sys.exit(1)

    base_name = os.path.splitext(source_path)[0]
    asm_file = f"{base_name}.asm"
    obj_file = f"{base_name}.obj"
    exe_file = args.output if args.output else f"{base_name}.exe"

    print(f"[1/3] Compiling Corvus Source '{source_path}' -> Assembly...")
    with open(source_path, "r") as f:
        code = f.read()

    tokens = tokenize(code)
    ast = Parser(tokens).parse()

    generator = AsmGenerator()
    generator.generate(ast)
    
    with open(asm_file, "w") as out:
        out.write(generator.build_full_asm())

    print(f"  --> Generated assembly: {asm_file}")
    nasm_path = find_tool(["nasm", "nasm.exe"])
    linker_path = find_tool(["clang", "clang.exe", "x86_64-w64-mingw32-gcc", "gcc", "gcc.exe"])

    if not nasm_path or not linker_path:
        print("\n[INFO] Assembly (.asm) generated successfully!")
        print("To build native .exe binaries, install NASM & GCC:")
        print("  - winget install NASM.NASM")
        print("  - winget install MartinStorsjo.LLVM-MinGW.UCRT\n")
        return


    rel_asm = asm_file
    rel_obj = obj_file
    rel_exe = exe_file

    print(f"[2/3] Assembling with NASM -> '{rel_obj}'...")
    res_nasm = subprocess.run([nasm_path, "-f", "win64", rel_asm, "-o", rel_obj])

    if res_nasm.returncode != 0:
        print("[ERROR] NASM Assembly Failed.")
        sys.exit(1)

    linker_name = os.path.basename(linker_path).upper()
    print(f"[3/3] Linking with {linker_name} -> '{rel_exe}'...")
    res_gcc = subprocess.run([linker_path, rel_obj, "-o", rel_exe])
    if res_gcc.returncode != 0:
        print("[ERROR] Linking Failed.")
        sys.exit(1)


    # Clean up temporary .obj file
    if os.path.exists(rel_obj):
        os.remove(rel_obj)
    if not args.keep_asm and os.path.exists(rel_asm):
        os.remove(rel_asm)

    print(f"\n[SUCCESS] Built native executable: {rel_exe}")

    if args.run:
        print(f"\n[RUN] Running {rel_exe}:\n" + "=" * 40)
        subprocess.run([rel_exe], shell=True)



if __name__ == "__main__":
    main()