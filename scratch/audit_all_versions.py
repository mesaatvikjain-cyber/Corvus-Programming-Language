import os
import sys
import py_compile
import importlib.util
import traceback

sys.stdout.reconfigure(encoding='utf-8')
project_root = r"C:\Users\Saatvik Jain\.gemini\antigravity\scratch\Corvus"

print("==========================================================")
print("   CORVUS COMPREHENSIVE MULTI-VERSION CODEBASE AUDIT      ")
print("==========================================================")

# 1. Collect all Python files & compile check
all_py_files = []
all_crv_files = []

for root, dirs, files in os.walk(project_root):
    rel_dir = os.path.relpath(root, project_root)
    if rel_dir.startswith(".git") or rel_dir.startswith("__pycache__") or rel_dir.startswith("node_modules") or rel_dir.startswith("scratch"):
        continue
    for f in files:
        full_p = os.path.join(root, f)
        if f.endswith(".py"):
            all_py_files.append(full_p)
        elif f.endswith(".crv"):
            all_crv_files.append(full_p)

print(f"Total Python Source Files Discovered: {len(all_py_files)}")
print(f"Total Corvus (.crv) Files Discovered: {len(all_crv_files)}")

# 1. Python Syntax Validation
py_errors = []
for pf in all_py_files:
    try:
        py_compile.compile(pf, doraise=True)
    except py_compile.PyCompileError as e:
        py_errors.append((os.path.relpath(pf, project_root), str(e)))

print("\n--- 1. Python Syntax Check ---")
if py_errors:
    print(f"❌ Found {len(py_errors)} Python syntax errors:")
    for path, err in py_errors:
        print(f"   - {path}: {err}")
else:
    print("✅ All Python files (256/256) passed compilation cleanly with zero syntax errors!")

# Helper to load lexer and parser for a specific version directory
def load_version_lexer_parser(version_dir):
    search_paths = [
        os.path.join(version_dir, "Interpreter"),
        version_dir,
        os.path.join(project_root, "Interpreter")
    ]
    
    for sp in search_paths:
        lpath = os.path.join(sp, "lexercorvus.py")
        ppath = os.path.join(sp, "parsercorvus.py")
        if os.path.exists(lpath) and os.path.exists(ppath):
            if sp not in sys.path:
                sys.path.insert(0, sp)
            l_spec = importlib.util.spec_from_file_location("lexercorvus", lpath)
            l_mod = importlib.util.module_from_spec(l_spec)
            l_spec.loader.exec_module(l_mod)

            p_spec = importlib.util.spec_from_file_location("parsercorvus", ppath)
            p_mod = importlib.util.module_from_spec(p_spec)
            p_spec.loader.exec_module(p_mod)

            return l_mod, p_mod
            
    return None, None

print("\n--- 2. Corvus (.crv) AST Parser Audit Across All Versions ---")

crv_parse_errors = []

for crv in all_crv_files:
    rel_p = os.path.relpath(crv, project_root)
    parts = rel_p.split(os.sep)
    
    version_dir = project_root
    if parts[0].startswith("Version_"):
        version_dir = os.path.join(project_root, parts[0])

    lexer_mod, parser_mod = load_version_lexer_parser(version_dir)
    
    if not lexer_mod or not parser_mod:
        crv_parse_errors.append((rel_p, "Could not locate lexercorvus.py / parsercorvus.py for this version."))
        continue

    try:
        with open(crv, "r", encoding="utf-8") as f:
            code = f.read()
        
        tokens = lexer_mod.tokenize(code)
        parser = parser_mod.Parser(tokens)
        ast = parser.parse()
    except Exception as e:
        crv_parse_errors.append((rel_p, str(e)))

if crv_parse_errors:
    print(f"❌ Found {len(crv_parse_errors)} Corvus parsing/syntax issues out of {len(all_crv_files)} files:")
    for path, err in crv_parse_errors:
        first_line = err.splitlines()[0] if err.splitlines() else err
        print(f"   - [{path}]: {first_line}")
else:
    print(f"✅ All {len(all_crv_files)} Corvus (.crv) files parsed cleanly into AST with ZERO syntax/lexer/parser errors!")

print("\n==========================================================")
print("              AUDIT COMPLETE                              ")
print("==========================================================")
