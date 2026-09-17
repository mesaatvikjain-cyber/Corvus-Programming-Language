import sys
import os
import shutil
import subprocess
import re

try:
    from Compiler_Core.Lexercompiler import tokenize
    from Compiler_Core.parser import Parser
    from Compiler_MacOS.compiler_asm_macos import AsmGeneratorMacOS
except ImportError:
    from Lexercompiler import tokenize
    from parser import Parser
    from compiler_asm_macos import AsmGeneratorMacOS


def find_tool(names):
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def compile_macos(source_path, output_path=None, run_after=False, keep_asm=False):
    base_name = os.path.splitext(source_path)[0]
    asm_file = f"{base_name}.asm"
    obj_file = f"{base_name}.o"
    exe_file = output_path if output_path else base_name

    print(f"[macOS Target] Compiling '{source_path}' -> Assembly (Mach-O)...")
    with open(source_path, "r", encoding="utf-8") as f:
        code = f.read()

    tokens = tokenize(code)
    ast = Parser(tokens).parse()

    generator = AsmGeneratorMacOS()
    generator.generate(ast)

    with open(asm_file, "w", encoding="utf-8") as out:
        out.write(generator.build_full_asm())

    print(f"  --> Generated assembly: {asm_file}")

    # Check if host platform is macOS
    is_macos_host = (sys.platform == "darwin")

    if not is_macos_host:
        print("\n[INFO] Target Mach-O Assembly (.asm) generated successfully!")
        print("To assemble and link on a macOS host, run:")
        print(f"  nasm -f macho64 {asm_file} -o {obj_file} && clang {obj_file} -o {exe_file} -lSystem\n")
        return asm_file

    nasm_path = find_tool(["nasm"])
    linker_path = find_tool(["clang", "gcc", "xcrun"])

    if not nasm_path or not linker_path:
        print("\n[INFO] macOS Assembly (.asm) generated successfully!")
        print("To build native macOS Mach-O binaries, install nasm & Xcode command line tools:\n  - brew install nasm\n  - xcode-select --install\n")
        return asm_file

    print(f"[2/3] Assembling with NASM -> '{obj_file}'...")
    res_nasm = subprocess.run([nasm_path, "-f", "macho64", asm_file, "-o", obj_file])

    if res_nasm.returncode != 0:
        print("[ERROR] NASM Assembly Failed.")
        sys.exit(1)

    linker_name = os.path.basename(linker_path).upper()
    print(f"[3/3] Linking with {linker_name} -> '{exe_file}'...")
    res_gcc = subprocess.run([linker_path, obj_file, "-o", exe_file, "-lSystem"])
    if res_gcc.returncode != 0:
        print("[ERROR] Linking Failed.")
        sys.exit(1)

    if os.path.exists(obj_file):
        os.remove(obj_file)
    if not keep_asm and os.path.exists(asm_file):
        os.remove(asm_file)

    print(f"\n[SUCCESS] Built native macOS executable: {exe_file}")

    if run_after:
        if not re.match(r'^[a-zA-Z0-9_\-./\\]+$', exe_file):
            print("[ERROR] Invalid executable file name.")
            sys.exit(1)
        print(f"\n[RUN] Running ./{exe_file}:\n" + "=" * 40)
        subprocess.run([f"./{exe_file}"], shell=True)

    return exe_file
