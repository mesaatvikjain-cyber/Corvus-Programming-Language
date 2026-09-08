import sys
import os
import shutil
import subprocess
import argparse

try:
    from Compiler_Core.Lexercompiler import tokenize
    from Compiler_Core.parser import Parser
    from Compiler_Windows.compiler_asm_win64 import AsmGeneratorWin64
except ImportError:
    from Lexercompiler import tokenize
    from parser import Parser
    from compiler_asm_win64 import AsmGeneratorWin64


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


def compile_windows(source_path, output_path=None, run_after=False, keep_asm=False):
    base_name = os.path.splitext(source_path)[0]
    asm_file = f"{base_name}.asm"
    obj_file = f"{base_name}.obj"
    exe_file = output_path if output_path else f"{base_name}.exe"

    print(f"[Windows Target] Compiling '{source_path}' -> Assembly (Win64)...")
    with open(source_path, "r", encoding="utf-8") as f:
        code = f.read()

    tokens = tokenize(code)
    ast = Parser(tokens).parse()

    generator = AsmGeneratorWin64()
    generator.generate(ast)

    with open(asm_file, "w", encoding="utf-8") as out:
        out.write(generator.build_full_asm())

    print(f"  --> Generated assembly: {asm_file}")
    nasm_path = find_tool(["nasm", "nasm.exe"])
    linker_path = find_tool(["clang", "clang.exe", "x86_64-w64-mingw32-gcc", "gcc", "gcc.exe"])

    if not nasm_path or not linker_path:
        print("\n[INFO] Windows Assembly (.asm) generated successfully!")
        print("To build native Windows .exe binaries, install NASM & GCC/Clang:\n  - winget install NASM.NASM\n  - winget install MartinStorsjo.LLVM-MinGW.UCRT\n")
        return asm_file

    print(f"[2/3] Assembling with NASM -> '{obj_file}'...")
    res_nasm = subprocess.run([nasm_path, "-f", "win64", asm_file, "-o", obj_file])

    if res_nasm.returncode != 0:
        print("[ERROR] NASM Assembly Failed.")
        sys.exit(1)

    linker_name = os.path.basename(linker_path).upper()
    print(f"[3/3] Linking with {linker_name} -> '{exe_file}'...")
    res_gcc = subprocess.run([linker_path, obj_file, "-o", exe_file])
    if res_gcc.returncode != 0:
        print("[ERROR] Linking Failed.")
        sys.exit(1)

    if os.path.exists(obj_file):
        os.remove(obj_file)
    if not keep_asm and os.path.exists(asm_file):
        os.remove(asm_file)

    print(f"\n[SUCCESS] Built native Windows executable: {exe_file}")

    if run_after:
        print(f"\n[RUN] Running {exe_file}:\n" + "=" * 40)
        subprocess.run([exe_file])

    return exe_file
