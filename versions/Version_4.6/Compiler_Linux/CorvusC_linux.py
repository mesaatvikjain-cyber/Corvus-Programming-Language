import sys
import os
import shutil
import subprocess

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

try:
    from Compiler_Core.Lexercompiler import tokenize
    from Compiler_Core.parser import Parser
    from Compiler_Linux.compiler_asm_linux import AsmGeneratorLinux
except ImportError:
    from Lexercompiler import tokenize
    from parser import Parser
    from compiler_asm_linux import AsmGeneratorLinux


def find_tool(names):
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def compile_linux(source_path, output_path=None, run_after=False, keep_asm=False):
    base_name = os.path.splitext(source_path)[0]
    asm_file = f"{base_name}.asm"
    obj_file = f"{base_name}.o"
    exe_file = output_path if output_path else base_name

    print(f"[Linux Target] Compiling '{source_path}' -> Assembly (ELF64)...")
    with open(source_path, "r", encoding="utf-8") as f:
        code = f.read()

    tokens = tokenize(code)
    ast = Parser(tokens).parse()

    generator = AsmGeneratorLinux()
    generator.generate(ast)

    with open(asm_file, "w", encoding="utf-8") as out:
        out.write(generator.build_full_asm())

    print(f"  --> Generated assembly: {asm_file}")

    # Check if host platform is Linux
    is_linux_host = sys.platform.startswith("linux")

    if not is_linux_host:
        print("\n[INFO] Target ELF64 Assembly (.asm) generated successfully!")
        print("To assemble and link on a Linux host, run:")
        print(f"  nasm -f elf64 {asm_file} -o {obj_file} && gcc {obj_file} -o {exe_file} -no-pie\n")
        return asm_file

    nasm_path = find_tool(["nasm"])
    linker_path = find_tool(["gcc", "clang", "ld"])

    if not nasm_path or not linker_path:
        print("\n[INFO] Linux Assembly (.asm) generated successfully!")
        print("To build native Linux ELF binaries, install nasm & gcc:\n  - sudo apt install nasm gcc  (Ubuntu/Debian)\n  - sudo dnf install nasm gcc  (Fedora/RHEL)\n")
        return asm_file

    print(f"[2/3] Assembling with NASM -> '{obj_file}'...")
    res_nasm = subprocess.run([nasm_path, "-f", "elf64", asm_file, "-o", obj_file])

    if res_nasm.returncode != 0:
        print("[ERROR] NASM Assembly Failed.")
        sys.exit(1)

    linker_name = os.path.basename(linker_path).upper()
    print(f"[3/3] Linking with {linker_name} -> '{exe_file}'...")
    res_gcc = subprocess.run([linker_path, obj_file, "-o", exe_file, "-no-pie"])
    if res_gcc.returncode != 0:
        # Fallback without -no-pie
        res_gcc = subprocess.run([linker_path, obj_file, "-o", exe_file])
        if res_gcc.returncode != 0:
            print("[ERROR] Linking Failed.")
            sys.exit(1)

    if os.path.exists(obj_file):
        os.remove(obj_file)
    if not keep_asm and os.path.exists(asm_file):
        os.remove(asm_file)

    print(f"\n[SUCCESS] Built native Linux executable: {exe_file}")

    if run_after:
        print(f"\n[RUN] Running ./{exe_file}:\n" + "=" * 40)
        subprocess.run([f"./{exe_file}"], shell=False)

    return exe_file
