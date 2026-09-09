import os
import sys
import py_compile
import subprocess
import traceback

sys.stdout.reconfigure(encoding='utf-8')

project_root = r"C:\Users\Saatvik Jain\.gemini\antigravity\scratch\Corvus"

print("==================================================")
print("   CORVUS DEEP PROJECT-WIDE BUG & SYNTAX AUDIT   ")
print("==================================================")

python_files = []
crv_files = []

for root, dirs, files in os.walk(project_root):
    rel_dir = os.path.relpath(root, project_root)
    if rel_dir.startswith(".git") or rel_dir.startswith("__pycache__") or rel_dir.startswith("node_modules") or rel_dir.startswith("scratch"):
        continue
    for f in files:
        full_path = os.path.join(root, f)
        if f.endswith(".py"):
            python_files.append(full_path)
        elif f.endswith(".crv"):
            crv_files.append(full_path)

print(f"Discovered {len(python_files)} Python files.")
print(f"Discovered {len(crv_files)} Corvus (.crv) files.")

# 1. Python Syntax Check
py_syntax_errors = []
for py_file in python_files:
    try:
        py_compile.compile(py_file, doraise=True)
    except py_compile.PyCompileError as e:
        rel_path = os.path.relpath(py_file, project_root)
        py_syntax_errors.append((rel_path, str(e)))

print("\n--- [1/3] Python Syntax Analysis ---")
if py_syntax_errors:
    print(f"Found {len(py_syntax_errors)} Python syntax errors:")
    for path, err in py_syntax_errors:
        print(f"  [ERR] [{path}]: {err}")
else:
    print("  [OK] All Python files passed py_compile syntax checks clean!")

# 2. Corvus Syntax Check across versions
print("\n--- [2/3] Corvus (.crv) Syntax & Parsing Analysis across Versions ---")
crv_errors = []

for crv_file in crv_files:
    rel_path = os.path.relpath(crv_file, project_root)
    interpreter_to_use = os.path.join(project_root, "Interpreter", "Corvus.py")
    
    parts = rel_path.split(os.sep)
    if parts[0].startswith("Version_"):
        v_dir = os.path.join(project_root, parts[0])
        cand1 = os.path.join(v_dir, "Interpreter", "Corvus.py")
        cand2 = os.path.join(v_dir, "Corvus.py")
        if os.path.exists(cand1):
            interpreter_to_use = cand1
        elif os.path.exists(cand2):
            interpreter_to_use = cand2

    if os.path.exists(interpreter_to_use):
        try:
            res = subprocess.run(
                [sys.executable, interpreter_to_use, "--check", crv_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            if res.returncode != 0:
                err_msg = res.stderr.strip() or res.stdout.strip()
                crv_errors.append((rel_path, interpreter_to_use, err_msg))
        except Exception as ex:
            crv_errors.append((rel_path, interpreter_to_use, str(ex)))

if crv_errors:
    print(f"Found {len(crv_errors)} Corvus syntax/linter issues out of {len(crv_files)} files:")
    for path, interp, err in crv_errors[:30]:
        rel_interp = os.path.relpath(interp, project_root)
        first_line = err.splitlines()[0] if err.splitlines() else err
        print(f"  [ERR] [{path}] (via {rel_interp}): {first_line}")
    if len(crv_errors) > 30:
        print(f"  ... and {len(crv_errors) - 30} more.")
else:
    print("  [OK] All Corvus (.crv) files passed syntax checking!")

# 3. Test Suites Execution across versions
print("\n--- [3/3] Running All Discovered Regression Test Suites ---")
test_suites = []
for root, dirs, files in os.walk(project_root):
    rel_dir = os.path.relpath(root, project_root)
    if rel_dir.startswith("scratch"): continue
    for f in files:
        if ("test" in f.lower() or "suite" in f.lower()):
            full_p = os.path.join(root, f)
            if f.endswith(".py") and f != "audit_project.py":
                test_suites.append(("py", full_p))

test_results = []
for stype, tfile in test_suites:
    rel_path = os.path.relpath(tfile, project_root)
    try:
        res = subprocess.run(
            [sys.executable, tfile],
            cwd=os.path.dirname(tfile),
            capture_output=True,
            text=True,
            timeout=15
        )
        if res.returncode == 0:
            test_results.append((rel_path, "PASS", ""))
        else:
            err_summary = res.stderr.strip() or res.stdout.strip()
            test_results.append((rel_path, "FAIL", err_summary))
    except Exception as ex:
        test_results.append((rel_path, "ERROR", str(ex)))

for path, status, detail in test_results:
    if status == "PASS":
        print(f"  [PASS] {path}")
    else:
        first_line = detail.splitlines()[-1] if detail.splitlines() else detail
        print(f"  [{status}] {path}: {first_line}")

print("\n==================================================")
print("               AUDIT SUMMARY COMPLETE             ")
print("==================================================")
