import sys
import os
import shutil
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Compiler_Core")))

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
    asm_file = f"{base_name}_linux.asm"
    obj_file = f"{base_name}_linux.o"
    exe_file = output_path if output_path else f"{base_name}_linux.elf"

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
    nasm_path = find_tool(["nasm"])
    linker_path = find_tool(["gcc", "clang", "ld"])

    if not nasm_path or not linker_path:
        print("\n[INFO] Linux Assembly (.asm) generated successfully!")
        print("To build native ELF binaries on Linux, install NASM and GCC/Clang:\n  - sudo apt install nasm build-essential\n")
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
        subprocess.run([f"./{exe_file}"], shell=True)

    return exe_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python CorvusC_linux.py <source.crv> [output.elf]")
        sys.exit(1)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    compile_linux(src, output_path=out, keep_asm=True)

if __name__ == "__main__":
    main()
