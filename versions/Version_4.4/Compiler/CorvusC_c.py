# Corvus C99 Compiler Driver (CorvusC - Target C)
# Compiles Corvus code directly into C99, then invokes GCC/Clang with -O3 optimizations

import sys
import os
import shutil
import subprocess
import argparse

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

try:
    from Compiler_Core.Lexercompiler import tokenize
    from Compiler_Core.parser import Parser
    from Compiler_Core.c_transpiler import CTranspiler
    from Interpreter.ast_optimizer import AstOptimizer
except ImportError:
    from Lexercompiler import tokenize
    from parser import Parser
    from c_transpiler import CTranspiler
    from ast_optimizer import AstOptimizer


def find_c_compiler():
    # Check standard PATH first
    candidates = ["clang", "gcc", "x86_64-w64-mingw32-gcc", "cl"]
    for c in candidates:
        p = shutil.which(c)
        if p:
            return p

    # Check common Windows locations
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    search_dirs = [
        os.path.join(local_app_data, "Microsoft", "WinGet", "Links"),
        r"C:\msys64\mingw64\bin",
        r"C:\msys64\ucrt64\bin",
        r"C:\MinGW\bin",
        r"C:\TDM-GCC-64\bin",
    ]

    winget_pkg_dir = os.path.join(local_app_data, "Microsoft", "WinGet", "Packages")
    if os.path.exists(winget_pkg_dir):
        for entry in os.listdir(winget_pkg_dir):
            if "LLVM" in entry or "MinGW" in entry:
                pkg_path = os.path.join(winget_pkg_dir, entry)
                for root, dirs, files in os.walk(pkg_path):
                    if os.path.basename(root).lower() == "bin":
                        search_dirs.insert(0, root)

    for d in search_dirs:
        for c in ["clang.exe", "gcc.exe"]:
            full = os.path.join(d, c)
            if os.path.exists(full):
                return full

    return None


def compile_c(source_path, output_path=None, run_after=False, keep_c=False, optimize=True):
    base_name = os.path.splitext(source_path)[0]
    c_file = f"{base_name}.c"
    exe_file = output_path if output_path else f"{base_name}.exe"

    print(f"[C99 Target] Compiling '{source_path}' -> C99 Native...")
    with open(source_path, "r", encoding="utf-8") as f:
        code = f.read()

    tokens = tokenize(code)
    ast = Parser(tokens).parse()

    if optimize:
        opt = AstOptimizer()
        ast = opt.optimize(ast)
        if opt.folded_constants > 0 or opt.pruned_branches > 0:
            print(f"  [Optimizer] Folded {opt.folded_constants} constant(s), pruned {opt.pruned_branches} dead branch(es)")

    transpiler = CTranspiler()
    c_code = transpiler.transpile(ast)

    with open(c_file, "w", encoding="utf-8") as f:
        f.write(c_code)

    print(f"  --> Generated C99 Source: {c_file}")

    compiler_path = find_c_compiler()
    if not compiler_path:
        print("\n[INFO] C99 source generated successfully!")
        print("To compile to native binary, install GCC or Clang (e.g. winget install MartinStorsjo.LLVM-MinGW.UCRT)")
        return c_file

    compiler_name = os.path.basename(compiler_path).upper()
    print(f"[2/2] Compiling with {compiler_name} (-O3) -> '{exe_file}'...")

    cmd = [compiler_path, "-O3", "-fno-lto", "-std=c99", c_file, "-o", exe_file, "-lm"]
    res = subprocess.run(cmd)

    if res.returncode != 0:
        print("[ERROR] C Compilation Failed.")
        sys.exit(1)

    if not keep_c and os.path.exists(c_file):
        os.remove(c_file)

    print(f"\n[SUCCESS] Built ultra-fast native executable: {exe_file}")

    if run_after:
        print(f"\n[RUN] Running {exe_file}:\n" + "=" * 40)
        try:
            subprocess.run([os.path.abspath(exe_file)])
        except Exception as e:
            print(f"[Note]: Executable created successfully. Direct execution note: {e}")

    return exe_file


def main():
    parser = argparse.ArgumentParser(description="Corvus C99 Compiler Driver (CorvusC --target=c)")
    parser.add_argument("source", help="Corvus source file (*.crv)")
    parser.add_argument("-o", "--output", help="Output binary path")
    parser.add_argument("--run", action="store_true", help="Execute binary immediately after building")
    parser.add_argument("--keep-c", action="store_true", help="Keep generated .c file")
    parser.add_argument("--no-opt", action="store_true", help="Disable AST optimization passes")

    args = parser.parse_args()
    compile_c(args.source, output_path=args.output, run_after=args.run, keep_c=args.keep_c, optimize=not args.no_opt)


if __name__ == "__main__":
    main()
