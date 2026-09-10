import sys
import os
from lexercorvus import tokenize
from parsercorvus import Parser
from evaluatorcorvus import Evaluator, Environment
from errors import CorvusError, explain_error
from repl import start_repl

def check_syntax(filepath: str):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    try:
        tokens = tokenize(code)
        parser = Parser(tokens)
        parser.parse()
        print(f"[Corvus Linter]: Syntax check passed for '{filepath}'.")
        sys.exit(0)
    except CorvusError as e:
        e.print_formatted(filepath, code)
        sys.exit(1)
    except Exception as e:
        print(f"[Corvus Syntax Error]: {e}", file=sys.stderr)
        sys.exit(1)

def run_file(filepath: str, ai_fix: bool = False, optimize: bool = True):
    if not filepath.endswith(".crv"):
        print(f"Error: File '{filepath}' must have a .crv extension.")
        sys.exit(1)

    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    try:
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()

        if optimize:
            from ast_optimizer import AstOptimizer
            ast = AstOptimizer().optimize(ast)

        global_env = Environment()
        evaluator = Evaluator(global_env)
        evaluator.current_file_path = filepath
        evaluator.evaluate(ast)

    except CorvusError as e:
        e.print_formatted(filepath, code, ai_fix=ai_fix)
        sys.exit(1)

    except Exception as e:
        print(f"[Corvus Internal Bug]: {e}", file=sys.stderr)
        sys.exit(1)

def compile_to_bytecode(filepath: str, output_path: str = None):
    """Compile Corvus source (.crv) into bytecode (.crvc)."""
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    if not output_path:
        base, _ = os.path.splitext(filepath)
        output_path = base + ".crvc"

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    try:
        from compiler_vm import BytecodeCompiler
        import bytecode
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = BytecodeCompiler(filename=filepath)
        code_obj = compiler.compile(ast)
        serialized = bytecode.serialize(code_obj)
        with open(output_path, "wb") as f_out:
            f_out.write(serialized)
        print(f"[Corvus Bytecode Compiler]: Successfully compiled '{filepath}' -> '{output_path}' ({len(serialized)} bytes)")
    except Exception as e:
        print(f"[Corvus Bytecode Compiler Error]: {e}", file=sys.stderr)
        sys.exit(1)

def disassemble_target(filepath: str):
    """Disassemble either .crv source or .crvc bytecode."""
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)

    import bytecode
    try:
        if filepath.endswith(".crvc"):
            with open(filepath, "rb") as f:
                data = f.read()
            code_obj = bytecode.deserialize(data)
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
            from compiler_vm import BytecodeCompiler
            tokens = tokenize(code)
            parser = Parser(tokens)
            ast = parser.parse()
            compiler = BytecodeCompiler(filename=filepath)
            code_obj = compiler.compile(ast)

        print(bytecode.disassemble(code_obj))
    except Exception as e:
        print(f"[Corvus Disassembler Error]: {e}", file=sys.stderr)
        sys.exit(1)

def run_vm(filepath: str):
    """Execute either a compiled .crvc bytecode file or a .crv source file directly in CorvusVM."""
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)

    import bytecode
    from vm import CorvusVM
    try:
        if filepath.endswith(".crvc"):
            with open(filepath, "rb") as f:
                data = f.read()
            code_obj = bytecode.deserialize(data)
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
            from compiler_vm import BytecodeCompiler
            tokens = tokenize(code)
            parser = Parser(tokens)
            ast = parser.parse()
            compiler = BytecodeCompiler(filename=filepath)
            code_obj = compiler.compile(ast)

        machine = CorvusVM()
        machine.run(code_obj)
    except Exception as e:
        print(f"[Corvus VM Runtime Error]: {e}", file=sys.stderr)
        sys.exit(1)

from formatter import format_file
from typechecker import TypeChecker
from benchmark import run_benchmark, run_profile

def run_typecheck(filepath: str):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
    try:
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        tc = TypeChecker(filepath, code)
        errors = tc.check(ast)
        if errors:
            print(f"\n==================================================")
            print(f"  Corvus Strict Type Check Failed ({len(errors)} error(s))")
            print(f"==================================================")
            for err in errors:
                err.print_formatted(filepath, code)
            sys.exit(1)
        else:
            print(f"[SUCCESS] Corvus Strict Type Check Passed: '{filepath}' is completely type safe!")
            sys.exit(0)
    except CorvusError as e:
        e.print_formatted(filepath, code)
        sys.exit(1)

def run_test_runner(directory: str = "."):
    test_files = []
    for root, dirs, files in os.walk(directory):
        if "corvus_modules" in root or ".git" in root:
            continue
        for f in files:
            if f.endswith(".crv") and ("test" in f.lower() or "suite" in f.lower()):
                if "input" in f.lower():
                    continue
                test_files.append(os.path.join(root, f))
    
    if not test_files:
        print("[INFO] No Corvus test suites (*test*.crv / *suite*.crv) found in this directory.")
        return

    print(f"==================================================")
    print(f"  Corvus Test Runner - Discovered {len(test_files)} Test Suite(s)")
    print(f"==================================================")

    passed = 0
    failed = 0
    for tf in test_files:
        print(f"\n[RUNNING] {tf} ...")
        try:
            with open(tf, "r", encoding="utf-8") as f:
                code = f.read()
            tokens = tokenize(code)
            parser = Parser(tokens)
            ast = parser.parse()
            from ast_optimizer import AstOptimizer
            ast = AstOptimizer().optimize(ast)
            global_env = Environment()
            evaluator = Evaluator(global_env)
            evaluator.current_file_path = tf
            evaluator.evaluate(ast)
            print(f"[PASS] {tf}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {tf} -> {e}")
            failed += 1

    print(f"\n==================================================")
    print(f"  Test Results: {passed} PASSED | {failed} FAILED")
    print(f"==================================================")
    if failed > 0:
        sys.exit(1)

def forward_to_cpm(args):
    cpm_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "cpm.py")
    if not os.path.exists(cpm_script):
        # Fallback local
        cpm_script = os.path.join(os.getcwd(), "bin", "cpm.py")
    import subprocess
    cmd = [sys.executable, cpm_script] + args
    subprocess.run(cmd)

def main():
    if len(sys.argv) < 2:
        start_repl()
        return

    # Check for --explain / -e
    if sys.argv[1] in ("--explain", "-e"):
        code = sys.argv[2] if len(sys.argv) > 2 else "all"
        explain_error(code)
        sys.exit(0)

    arg1 = sys.argv[1]

    # CPM package manager integration commands
    if arg1 in ("init", "install", "list", "remove"):
        forward_to_cpm(sys.argv[1:])
        return

    # Code Formatter (corvus fmt)
    if arg1 == "fmt":
        if len(sys.argv) < 3:
            print("Usage: corvus fmt <file.crv> [--check]")
            sys.exit(1)
        check_only = "--check" in sys.argv
        target_file = [a for a in sys.argv[2:] if a != "--check"][0]
        success = format_file(target_file, check_only=check_only)
        sys.exit(0 if success else 1)

    # Test Runner (corvus test)
    if arg1 == "test":
        target_dir = sys.argv[2] if len(sys.argv) > 2 else "."
        run_test_runner(target_dir)
        return

    # Strict Type Checker (corvus --strict)
    if arg1 in ("--strict", "-s"):
        if len(sys.argv) < 3:
            print("Usage: corvus --strict <file.crv>")
            sys.exit(1)
        run_typecheck(sys.argv[2])
        return

    # High-Precision Benchmarking (corvus bench)
    if arg1 == "bench":
        if len(sys.argv) < 3:
            print("Usage: corvus bench <file.crv> [iterations] [--no-opt]")
            sys.exit(1)
        target = sys.argv[2]
        iters = 50
        no_opt = "--no-opt" in sys.argv
        for a in sys.argv[3:]:
            if a.isdigit():
                iters = int(a)
        run_benchmark(target, iterations=iters, optimize=not no_opt)
        return

    # Execution Profiler (corvus profile)
    if arg1 == "profile":
        if len(sys.argv) < 3:
            print("Usage: corvus profile <file.crv>")
            sys.exit(1)
        run_profile(sys.argv[2])
        return

    # Bytecode Compiler (corvus compile <file.crv> [-o output.crvc])
    if arg1 == "compile":
        if len(sys.argv) < 3:
            print("Usage: corvus compile <file.crv> [-o output.crvc]")
            sys.exit(1)
        src_file = sys.argv[2]
        out_file = None
        if "-o" in sys.argv:
            o_idx = sys.argv.index("-o")
            if o_idx + 1 < len(sys.argv):
                out_file = sys.argv[o_idx + 1]
        compile_to_bytecode(src_file, out_file)
        return

    # Bytecode Disassembler (corvus dis <file.crv | file.crvc>)
    if arg1 == "dis":
        if len(sys.argv) < 3:
            print("Usage: corvus dis <file.crv | file.crvc>")
            sys.exit(1)
        disassemble_target(sys.argv[2])
        return

    # Virtual Machine Direct Run (corvus --vm <file.crv | file.crvc>)
    if arg1 in ("--vm", "-vm"):
        if len(sys.argv) < 3:
            print("Usage: corvus --vm <file.crv | file.crvc>")
            sys.exit(1)
        run_vm(sys.argv[2])
        return

    if arg1 in ("--repl", "-r"):
        start_repl()
    elif arg1 in ("--check", "-c"):
        if len(sys.argv) < 3:
            print("Usage: python Corvus.py --check <filename.crv>")
            sys.exit(1)
        check_syntax(sys.argv[2])
    elif arg1 in ("--help", "-h"):
        print("Corvus Language Launcher & Toolchain v4.5.0")
        print("Usage:")
        print("  corvus                                   Launch interactive REPL")
        print("  corvus <file.crv>                        Execute Corvus source file")
        print("  corvus <file.crvc>                       Execute precompiled Corvus bytecode")
        print("  corvus compile <file.crv> [-o out.crvc]  Compile Corvus source to binary bytecode")
        print("  corvus dis <file.crv | file.crvc>        Disassemble Corvus source or bytecode")
        print("  corvus --vm <file.crv | file.crvc>       Execute using Corvus Bytecode Virtual Machine")
        print("  corvus <file.crv> --ai-fix               Execute with AI-grade diagnostic solutions")
        print("  corvus <file.crv> --no-opt               Disable AST optimization engine")
        print("  corvus --strict <file.crv>               Run static type analyzer & strict linter")
        print("  corvus fmt <file.crv> [--check]          Canonical code auto-formatter")
        print("  corvus test [dir]                        Auto-discover and run all test suites")
        print("  corvus bench <file.crv> [iters]          High-precision nanosecond benchmark suite")
        print("  corvus profile <file.crv>                Statement execution and AST node profiler")
        print("  corvus init                              Initialize a new Corvus project manifest")
        print("  corvus install [pkg]                     Install Corvus packages (local or global)")
        print("  corvus list                              List installed packages")
        print("  corvus remove <pkg>                      Uninstall a package")
        print("  corvus --explain [CODE]                  Explain an error code (or all)")
        print("  corvus --check <file.crv>                Basic syntax check mode")
        print("  corvus --repl                            Launch interactive REPL")
    else:
        # Check for --ai-fix flag anywhere in args
        ai_fix = "--ai-fix" in sys.argv
        args_filtered = [a for a in sys.argv[1:] if a != "--ai-fix"]
        if args_filtered:
            target = args_filtered[0]
            if target.endswith(".crvc"):
                run_vm(target)
            else:
                run_file(target, ai_fix=ai_fix)
        else:
            start_repl()

if __name__ == "__main__":
    main()
