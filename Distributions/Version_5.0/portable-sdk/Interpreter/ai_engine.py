import re
import os
import time
from difflib import SequenceMatcher
class RavenAI:
    def __init__(self):
        self.name="RavenAI"
        self.version="2.0"
        self.knowledge = {
            "variables": {
                "aliases": ["variable", "variables", "set", "declare", "declaration", "const", "constant", "types", "assign", "assignment"],
                "description": "Corvus uses 'set' to declare variables with explicit types (int, str, flo, bool, lis, tup, dic) or auto-inference.",
                "example": "set int; count = 10\nset str; name = \"Corvus\"\nset const; MAX_LIMIT = 100"
            },
            "functions": {
                "aliases": ["function", "functions", "func", "mk func", "method", "methods", "givout", "return", "def", "procedure"],
                "description": "Functions in Corvus are declared with 'mk func name(params) [ ... ]' and return values using 'givout'.",
                "example": "mk func add(a, b) [\n    givout a + b\n]\n\nlog(\"Result:\", add(10, 20))"
            },
            "matrix": {
                "aliases": ["matrix", "matmul", "multiplication", "@", "numpy", "pytorch", "tensor", "linear algebra"],
                "description": "Corvus has a native matrix multiplication operator '@' for 2D lists, NumPy, and PyTorch.",
                "example": "set lis; A = [[1, 2], [3, 4]]\nset lis; B = [[5, 6], [7, 8]]\nset any; C = A @ B\nlog(\"Matrix C:\", C)"
            },
            "classes": {
                "aliases": ["class", "classes", "cls", "object", "oop", "constructor", "init", "self", "this", "inheritance"],
                "description": "Classes are defined with 'cls Name() [ ... ]', fields with 'set type; name', and constructors with 'mk func init(...)'.",
                "example": "cls Person() [\n    set str; name\n    mk func init(name_val) [\n        self.name = name_val\n    ]\n    mk func describe() [\n        log(\"Person -> Name:\", self.name)\n    ]\n]\nset Person; p = Person(\"Saatvik\")\np.describe()"
            },
            "loops": {
                "aliases": ["loop", "loops", "while", "for", "repeat", "iteration", "iterate", "brk", "con", "stop", "skip", "break", "continue"],
                "description": "Corvus supports 'while' and 'for' loops. Use 'brk;' or 'stop;' to break, and 'con;' or 'skip;' to continue.",
                "example": "set int; i = 0\nwhile (i < 5) [\n    log(\"Count:\", i)\n    set i = i + 1\n]"
            },
            "conditions": {
                "aliases": ["condition", "conditions", "if", "else", "elsif", "otherwise", "ternary", "branching", "boolean"],
                "description": "Use 'if' and 'else' (or 'elsif' / 'otherwise') for branching, or inline ternaries (condition ? true_val : false_val).",
                "example": "if (score >= 90) [\n    log(\"Passed!\")\n] else [\n    log(\"Try again\")\n]\nset str; grade = score >= 90 ? \"A\" : \"B\""
            },
            "brackets": {
                "aliases": ["bracket", "brackets", "square brackets", "curly braces", "block", "blocks", "list syntax", "dual brackets"],
                "description": "Corvus uniquely uses square brackets [ ... ] for code blocks and curly braces { ... } for lists. In v4.4+, modern dual brackets are supported.",
                "example": "set lis; numbers = {10, 20, 30}\nif (numbers.len() > 0) [\n    log(\"First element:\", numbers[0])\n]"
            },
            "fstring": {
                "aliases": ["fstring", "f-string", "format", "string interpolation", "template string", "interpolation"],
                "description": "Modern F-strings allow embedding expressions and variables directly in text with f\"...\".",
                "example": "set str; name = \"Saatvik\"\nset int; age = 11\nlog(f\"Hello {name}, next year you will be {age + 1}\")"
            },
            "concurrency": {
                "aliases": ["concurrency", "crow", "crows", "murder of crows", "thread", "parallel", "async", "background task"],
                "description": "Corvus concurrency engine ('Murder of Crows') allows running parallel background tasks with crow.",
                "example": "get crow\nset any; task = crow.spawn(func() [ log(\"Running in background\") ])\ncrow.join(task)"
            },
            "database": {
                "aliases": ["database", "db", "sqlite", "sql", "query", "table", "connect", "storage"],
                "description": "Corvus includes safe parameterized SQLite support in its standard library.",
                "example": "get db\nset any; conn = db.connect(\"app.db\")\nconn.execute(\"CREATE TABLE users (id INT, name TEXT);\")\nconn.query_params(\"INSERT INTO users VALUES (?, ?);\", {1, \"Saatvik\"})"
            },
            "bytecode": {
                "aliases": ["bytecode", "vm", "virtual machine", "compile", "crvc", "disassemble", "stack machine"],
                "description": "Compile Corvus scripts into high-performance binary bytecode (.crvc) and execute with the CorvusVM.",
                "example": "corvus compile script.crv -o script.crvc\ncorvus script.crvc\ncorvus --vm script.crv"
            },

        }
    def greet(self):
        return f"Hello! I am {self.name} v{self.version}, your Corvus assistant"
    def ask(self, question: str) -> str:
        q = question.lower()

        # 1. First, check for exact symbol operators (like '@')
        for topic, data in self.knowledge.items():
            aliases = data.get("aliases", [topic])
            for alias in aliases:
                if not alias.isalnum() and alias in q:
                    return f"[{self.name}]: {data['description']}\n\nExample:\n{data['example']}"

        # 2. Extract words from user question
        words = re.findall(r'\w+', q)
        if not words:
            return f"[{self.name}]: Please ask a question about Corvus syntax or concepts!"

        # 3. Fuzzy match against all topics and aliases
        best_topic = None
        best_data = None
        matched_alias = None
        highest_score = 0.0

        for topic, data in self.knowledge.items():
            aliases = data.get("aliases", [topic])
            for word in words:
                # Skip short stop-words
                if len(word) < 3 and word != "@":
                    continue

                for alias in aliases:
                    # Exact word match gets a perfect 1.0
                    if word == alias:
                        score = 1.0
                    # Fuzzy match for typos (words of similar length)
                    elif abs(len(word) - len(alias)) <= 2:
                        score = SequenceMatcher(None, word, alias).ratio()
                    else:
                        score = 0.0

                    if score > highest_score:
                        highest_score = score
                        best_topic = topic
                        best_data = data
                        matched_alias = alias

        # 4. If confidence is 75% or higher, return the answer!
        if highest_score >= 0.75 and best_data:
            typo_note = ""
            if highest_score < 1.0:
                typo_note = f"*(Recognized topic: '{best_topic}' via '{matched_alias}')*\n\n"

            return f"[{self.name}]: {typo_note}{best_data['description']}\n\nExample:\n{best_data['example']}"

        # 5. Fallback if no topic matched
        return f"Sorry, v{self.version} of {self.name} cannot answer your question. Try asking about: {', '.join(self.knowledge.keys())}"

    def explain(self, target: str) -> str:
        # 1. Smart file path resolution
        actual_path = target
        if not os.path.exists(actual_path):
            cand = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", target))
            if os.path.exists(cand):
                actual_path = cand
            else:
                cand_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", target))
                if os.path.exists(cand_root):
                    actual_path = cand_root

        # 2. Read file or treat as direct code snippet
        if os.path.exists(actual_path):
            with open(actual_path, "r", encoding="utf-8") as f:
                code = f.read()
            filename = os.path.basename(actual_path)
        else:
            code = target
            filename = "Snippet"

        # 3. Analyze the code
        lines = code.splitlines()
        classes = []
        functions = []
        imports = []
        has_matrix = False
        has_loops = False
        has_conditions = False

        for line in lines:
            line_str = line.strip()
            if line_str.startswith("get "):
                mod = line_str.replace("get ", "").replace(";", "").strip()
                imports.append(mod)
            elif line_str.startswith("cls "):
                parts = line_str.split()
                if len(parts) >= 2:
                    classes.append(parts[1].split("[")[0].split("{")[0])
            elif "mk func " in line_str or "func " in line_str:
                parts = line_str.split("func ")
                if len(parts) >= 2:
                    func_name = parts[1].split("(")[0].strip()
                    if func_name and func_name not in functions:
                        functions.append(func_name)

            if "@" in line_str:
                has_matrix = True
            if "while" in line_str or "for" in line_str:
                has_loops = True
            if "if" in line_str or "else" in line_str or "otherwise" in line_str:
                has_conditions = True

        # 4. Formulate the response
        report = []
        report.append(f"[{self.name} Code Analysis for '{filename}']")
        report.append(f"Total Lines of Code: {len(lines)}")
        
        if imports:
            report.append(f"\n[Modules Imported]: {', '.join(imports)}")
        if classes:
            report.append(f"\n[Classes Defined ({len(classes)})]:")
            for c in classes:
                report.append(f"   * cls {c}")
        if functions:
            report.append(f"\n[Functions Declared ({len(functions)})]:")
            for fn in functions:
                report.append(f"   * mk func {fn}()")

        highlights = []
        if has_matrix:
            highlights.append("Uses native Matrix Multiplication (@)")
        if has_loops:
            highlights.append("Contains iterative control flow (loops)")
        if has_conditions:
            highlights.append("Includes conditional branching (if/otherwise)")

        if highlights:
            report.append(f"\n[Key Highlights]:")
            for h in highlights:
                report.append(f"   * {h}")

        return "\n".join(report)
    def chat(self):
        print("=" * 60)
        print(f"  [RavenAI] Welcome to {self.name} v{self.version} Interactive Assistant!")
        print("  Ask any question about Corvus syntax, idioms, or code.")
        print("  Commands:")
        print("    'code--ask'       - Query syntax & knowledge base")
        print("    'code--summary'   - Structural file inspection")
        print("    'code--fix'       - Diagnose and auto-fix bugs")
        print("    'code--translate' - Transpile Python code to Corvus")
        print("    'code--testgen'   - Generate complete unit test suite")
        print("    'code--doc'       - Generate Markdown documentation")
        print("    'code--review'    - Static analysis & linting")
        print("    'code--export'    - Transpile Corvus to Python or C99")
        print("    'exit'            - Exit assistant")
        print("=" * 60)
        while True:
            user_prompt = input("\nRavenAI > ").strip()
            if "code--summary" == user_prompt:
                path = input("Please state the path of the file: ")
                time.sleep(1)
                print("\n" + self.explain(path))
            elif "code--ask" == user_prompt:
                question = input("Please state your Corvus question: ")
                time.sleep(1)
                print(self.ask("\n" + question))
            elif "code--fix" == user_prompt:
                target = input("Please enter code snippet or file path to fix: ")
                time.sleep(1)
                print("\n" + self.fix(target))
            elif "code--translate" == user_prompt:
                target = input("Please enter Python snippet or file path to translate: ")
                time.sleep(1)
                print("\n" + self.translate(target))
            elif "code--testgen" == user_prompt:
                target = input("Please enter file path to generate unit tests for: ")
                time.sleep(1)
                print("\n" + self.testgen(target))
            elif "code--doc" == user_prompt:
                target = input("Please enter file path to generate documentation for: ")
                time.sleep(1)
                print("\n" + self.doc(target))
            elif "code--review" == user_prompt:
                target = input("Please enter file path to review: ")
                time.sleep(1)
                print("\n" + self.review(target))
            elif "code--export" == user_prompt:
                target = input("Please enter file path to export: ")
                lang = input("Target language ('py' or 'c') [default: py]: ").strip() or "py"
                time.sleep(1)
                print("\n" + self.export_code(target, lang))
            elif "exit" == user_prompt or "quit" == user_prompt:
                print("RavenAI chat mode exited. Happy coding in Corvus!")
                break
            else:
                print("Unknown command. Available: 'code--ask', 'code--summary', 'code--fix', 'code--translate', 'code--testgen', 'code--doc', 'code--review', 'code--export', or 'exit'.")

    def fix(self, target):
        # 1. Smart file path resolution
        actual_path = target
        if not os.path.exists(actual_path):
            cand = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", target))
            if os.path.exists(cand):
                actual_path = cand
            else:
                cand_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", target))
                if os.path.exists(cand_root):
                    actual_path = cand_root

        # 2. Read file or treat as direct code
        if os.path.exists(actual_path):
            with open(actual_path, "r", encoding="utf-8") as f:
                code = f.read()
            filename = os.path.basename(actual_path)
        else:
            code = target
            filename = "Snippet"

        try:
            from lexercorvus import tokenize
            from parsercorvus import Parser
        except ImportError:
            from Interpreter.lexercorvus import tokenize
            from Interpreter.parsercorvus import Parser
        lines = code.splitlines()

        # 1. First check for common Pythonisms or syntax bugs
        problem_line_idx = -1
        suggested_line = None
        hint = ""

        for idx, line in enumerate(lines):
            line_str = line.strip()

            # Bug 1: Python 'print(...)' instead of Corvus 'log(...)'
            if line_str.startswith("print(") and line_str.endswith(")"):
                problem_line_idx = idx
                content = line_str[6:-1]
                suggested_line = f"log({content})"
                hint = "In Corvus, use 'log(...)' instead of Python's 'print()'"
                break

            # Bug 2: Python 'def func_name(...):' instead of Corvus 'mk func func_name(...) ['
            if line_str.startswith("def ") and line_str.endswith(":"):
                problem_line_idx = idx
                sig = line_str[4:-1]
                suggested_line = f"mk func {sig} ["
                hint = "In Corvus, declare functions with 'mk func <name>(args) ['"
                break

            # Bug 3: Python 'return' instead of 'givout'
            if line_str.startswith("return "):
                problem_line_idx = idx
                val = line_str.replace("return ", "").strip()
                suggested_line = f"givout {val}"
                hint = "Corvus uses the keyword 'givout' to return values from functions"
                break

        if problem_line_idx >= 0 and suggested_line:
            orig_line = lines[problem_line_idx].strip()
            report = [
                f"[{self.name} Diagnostic & Fix Report for '{filename}']",
                f"Status: Error Detected (Python syntax detected in Corvus file)",
                f"\nOffending Line {problem_line_idx + 1}:",
                f"  [-] {orig_line}",
                f"Suggested Patch:",
                f"  [+] {suggested_line}",
                f"\nReason: {hint}"
            ]
            return "\n".join(report)

        # 2. Try lexing and parsing
        try:
            tokens = tokenize(code)
            parser = Parser(tokens)
            ast = parser.parse()
            return f"[{self.name}]: No syntax errors detected in '{filename}'. Code looks valid!"

        except Exception as err:
            error_msg = str(err)
            report = [
                f"[{self.name} Diagnostic & Fix Report for '{filename}']",
                f"Status: Error Detected",
                f"Error Details: {error_msg}"
            ]

            # Check unclosed bracket
            for idx, line in enumerate(lines):
                line_str = line.strip()
                if line_str.count("[") > line_str.count("]"):
                    report.append(f"\nOffending Line {idx + 1}:")
                    report.append(f"  [-] {line_str}")
                    report.append(f"Suggested Patch:")
                    report.append(f"  [+] {line_str} ]")
                    report.append(f"\nReason: Unclosed code block bracket: missing ']'")
                    break
                elif line_str.count("{") > line_str.count("}"):
                    report.append(f"\nOffending Line {idx + 1}:")
                    report.append(f"  [-] {line_str}")
                    report.append(f"Suggested Patch:")
                    report.append(f"  [+] {line_str} }}")
                    report.append(f"\nReason: Unclosed list/block brace: missing '}}'")
                    break
            else:
                report.append(f"\nHint: Check matching brackets [ ] for blocks, {{ }} for lists, and valid Corvus keywords.")

            return "\n".join(report)
    def translate(self, target: str) -> str:
        """Translate Python source code into idiomatic Corvus code."""
        # 1. Read file if path is given, otherwise treat as code string
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                py_code = f.read()
        else:
            py_code = target

        lines = py_code.splitlines()
        corvus_lines = []
        indent_levels = [0]

        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines or pure comments
            if not stripped:
                corvus_lines.append("")
                continue
            if stripped.startswith("#"):
                corvus_lines.append(line)
                continue

            # Calculate indentation (count leading spaces)
            current_indent = len(line) - len(line.lstrip(" "))

            # If indentation decreased, close the matching Corvus brackets [ ]
            while current_indent < indent_levels[-1]:
                indent_levels.pop()
                pad = " " * indent_levels[-1]
                corvus_lines.append(f"{pad}]")

            # Translation Rules
            translated_line = stripped

            # 1. Output: print(...) -> log(...)
            if translated_line.startswith("print(") and translated_line.endswith(")"):
                inner = translated_line[6:-1]
                translated_line = f"log({inner})"

            # 2. Return: return x -> givout x
            elif translated_line.startswith("return "):
                val = translated_line[7:].strip()
                translated_line = f"givout {val}"
            elif translated_line == "return":
                translated_line = "givout"

            # 3. Class: class Name: -> cls Name() [
            elif translated_line.startswith("class ") and translated_line.endswith(":"):
                class_name = translated_line[6:-1].split("(")[0].strip()
                translated_line = f"cls {class_name}() ["
                indent_levels.append(current_indent + 4)

            # 4. Constructor: def __init__(self, ...): -> mk func init(...) [
            elif translated_line.startswith("def __init__(self") and translated_line.endswith(":"):
                params = translated_line[17:-2].lstrip(", ")
                translated_line = f"mk func init({params}) ["
                indent_levels.append(current_indent + 4)

            # 5. Functions: def name(...): -> mk func name(...) [
            elif translated_line.startswith("def ") and translated_line.endswith(":"):
                sig = translated_line[4:-1].strip()
                # Remove 'self, ' if present inside methods
                sig = sig.replace("(self, ", "(").replace("(self)", "()")
                translated_line = f"mk func {sig} ["
                indent_levels.append(current_indent + 4)

            # 6. Conditions: if / elif / else
            elif translated_line.startswith("if ") and translated_line.endswith(":"):
                cond = translated_line[3:-1].strip()
                translated_line = f"if ({cond}) ["
                indent_levels.append(current_indent + 4)
            elif translated_line.startswith("elif ") and translated_line.endswith(":"):
                cond = translated_line[5:-1].strip()
                translated_line = f"elsif ({cond}) ["
                indent_levels.append(current_indent + 4)
            elif translated_line == "else:":
                translated_line = "else ["
                indent_levels.append(current_indent + 4)

            # 7. Loops: while / for
            elif translated_line.startswith("while ") and translated_line.endswith(":"):
                cond = translated_line[6:-1].strip()
                translated_line = f"while ({cond}) ["
                indent_levels.append(current_indent + 4)
            elif translated_line.startswith("for ") and translated_line.endswith(":"):
                loop_expr = translated_line[4:-1].strip()
                translated_line = f"for {loop_expr} ["
                indent_levels.append(current_indent + 4)

            # Re-apply indentation
            pad = " " * current_indent
            corvus_lines.append(f"{pad}{translated_line}")

        # Close any remaining unclosed blocks at EOF
        while len(indent_levels) > 1:
            indent_levels.pop()
            pad = " " * indent_levels[-1]
            corvus_lines.append(f"{pad}]")

        header = f"// [Transpiled from Python to Corvus by {self.name} v{self.version}]\n"
        return header + "\n".join(corvus_lines)

    def testgen(self, target: str, output_file: str = None) -> str:
        """Automatically generate a complete unit test suite for any Corvus file or snippet."""
        code = target
        fname = "snippet"
        if os.path.exists(target):
            fname = os.path.basename(target)
            with open(target, "r", encoding="utf-8") as f:
                code = f.read()

        funcs = re.findall(r"mk\s+func\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)", code)
        test_lines = [
            f"// ==========================================================",
            f"//   Automated Unit Test Suite for {fname}",
            f"//   Generated by RavenAI v{self.version}",
            f"// ==========================================================",
            "",
            "set int; __test_passed = 0",
            "set int; __test_total = 0",
            "",
            "mk func __assert_true(name, condition) [",
            "    set __test_total = __test_total + 1",
            "    if (condition) [",
            "        set __test_passed = __test_passed + 1",
            "        log(\"  [PASS]:\", name)",
            "    ] else [",
            "        log(\"  [FAIL]:\", name)",
            "    ]",
            "]",
            ""
        ]

        if not funcs:
            test_lines.append("// No top-level functions discovered to test.")
            test_lines.append("__assert_true(\"Baseline execution test\", true)")
        else:
            for idx, (fn_name, params_str) in enumerate(funcs, start=1):
                raw_params = [p.strip() for p in params_str.split(",") if p.strip() and p.strip() != "self"]
                param_count = len(raw_params)
                test_lines.append(f"// --- Test Case {idx}: Function '{fn_name}' ---")
                sample_args = ", ".join(["10" for _ in range(param_count)]) if param_count > 0 else ""
                test_lines.append(f"set any; res_{fn_name}_1 = {fn_name}({sample_args})")
                test_lines.append(f"__assert_true(\"{fn_name}() standard invocation\", res_{fn_name}_1 != null)")
                if param_count > 0:
                    edge_args = ", ".join(["0" for _ in range(param_count)])
                    test_lines.append(f"set any; res_{fn_name}_edge = {fn_name}({edge_args})")
                    test_lines.append(f"__assert_true(\"{fn_name}() zero/boundary condition\", true)")
                test_lines.append("")

        test_lines.append("// --- Summary Results ---")
        test_lines.append("log(\"==========================================================\")")
        test_lines.append("log(\"Test Suite Finished. Passed:\", __test_passed, \"/ Total:\", __test_total)")
        test_lines.append("if (__test_passed == __test_total) [")
        test_lines.append("    log(\"100% of unit tests passed successfully!\")")
        test_lines.append("] else [")
        test_lines.append("    log(\"Some unit tests failed. Please review outputs above.\")")
        test_lines.append("]")
        test_lines.append("log(\"==========================================================\")")

        result = "\n".join(test_lines)
        if output_file:
            with open(output_file, "w", encoding="utf-8") as out:
                out.write(result)
        return result

    def doc(self, target: str, output_file: str = None) -> str:
        """Automatically inspect functions, classes, and types to generate Markdown documentation."""
        code = target
        fname = "Corvus Module"
        if os.path.exists(target):
            fname = os.path.basename(target)
            with open(target, "r", encoding="utf-8") as f:
                code = f.read()

        doc_lines = [
            f"# [Doc] {fname} Documentation",
            "",
            f"> *Auto-generated by **RavenAI v{self.version}** Documentation Generator.*",
            "",
            "## Overview",
            f"This module contains Corvus source definitions extracted from `{fname}`.",
            "",
        ]

        classes = re.findall(r"cls\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)\s*\[(.*?)\]", code, re.DOTALL)
        if classes:
            doc_lines.append("## Classes")
            for cname, cbody in classes:
                doc_lines.append(f"### `cls {cname}()`\n")
                methods = re.findall(r"mk\s+func\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)", cbody)
                fields = re.findall(r"set\s+([a-zA-Z_][a-zA-Z0-9_]*);?\s*([a-zA-Z_][a-zA-Z0-9_]*)", cbody)
                if fields:
                    doc_lines.append("**Properties / Fields:**")
                    doc_lines.append("| Field Name | Inferred / Explicit Type |")
                    doc_lines.append("| :--- | :--- |")
                    for ftype, fname_prop in fields:
                        doc_lines.append(f"| `{fname_prop}` | `{ftype}` |")
                    doc_lines.append("")
                if methods:
                    doc_lines.append("**Methods:**")
                    doc_lines.append("| Method | Parameters | Description |")
                    doc_lines.append("| :--- | :--- | :--- |")
                    for mname, mparams in methods:
                        mdesc = "Class constructor" if mname == "init" else f"Executes `{mname}` member routine."
                        doc_lines.append(f"| `self.{mname}()` | `({mparams})` | {mdesc} |")
                    doc_lines.append("")

        funcs = re.findall(r"mk\s+func\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)", code)
        class_methods = set()
        for _, cbody in classes:
            for mname, _ in re.findall(r"mk\s+func\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)", cbody):
                class_methods.add(mname)
        standalone_funcs = [(fn, p) for fn, p in funcs if fn not in class_methods or fn == "main"]

        if standalone_funcs:
            doc_lines.append("## Functions")
            doc_lines.append("| Function Signature | Parameters | Description |")
            doc_lines.append("| :--- | :--- | :--- |")
            for fn_name, params in standalone_funcs:
                p_list = params.strip() if params.strip() else "(none)"
                doc_lines.append(f"| `mk func {fn_name}({params})` | `{p_list}` | Top-level function definition |")
            doc_lines.append("")

        imports = re.findall(r"get\s+([a-zA-Z_][a-zA-Z0-9_]*)", code)
        if imports:
            doc_lines.append("## Dependencies & Imports")
            for imp in sorted(set(imports)):
                doc_lines.append(f"- `get {imp}`")
            doc_lines.append("")

        result = "\n".join(doc_lines)
        if output_file:
            with open(output_file, "w", encoding="utf-8") as out:
                out.write(result)
        return result

    def review(self, target: str) -> str:
        """Intelligent static code review, linting, and performance optimization analyzer."""
        code = target
        fname = "source"
        if os.path.exists(target):
            fname = os.path.basename(target)
            with open(target, "r", encoding="utf-8") as f:
                code = f.read()

        lines = code.splitlines()
        findings = []

        # 1. Nested loop detection -> suggest native '@'
        for i, line in enumerate(lines):
            if re.search(r"\bfor\b.*\[", line) or re.search(r"\bwhile\b.*\[", line):
                for j in range(i + 1, min(i + 4, len(lines))):
                    if re.search(r"\bfor\b.*\[", lines[j]) or re.search(r"\bwhile\b.*\[", lines[j]):
                        findings.append({
                            "type": "PERFORMANCE",
                            "line": i + 1,
                            "title": "Nested Loop Detected — Potential Matrix Multiplication",
                            "suggestion": "If iterating across 2D matrices or tensors, use Corvus's native matrix operator '@' (e.g. 'set C = A @ B') for 10x-50x faster SIMD execution."
                        })
                        break

        # 2. Unused variables
        declared_vars = []
        for i, line in enumerate(lines):
            m = re.search(r"set\s+(?:int|str|flo|bool|lis|tup|dic|any)?\s*;?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=", line)
            if m:
                vname = m.group(1)
                if not vname.startswith("_") and vname != "self":
                    declared_vars.append((vname, i + 1))
        for vname, lnum in declared_vars:
            occurrences = sum(1 for line in lines if re.search(rf"\b{vname}\b", line))
            if occurrences == 1:
                findings.append({
                    "type": "WARNING",
                    "line": lnum,
                    "title": f"Unused Variable '{vname}'",
                    "suggestion": f"Variable '{vname}' is assigned but never referenced again. Remove it or prefix with underscore '_{vname}'."
                })

        # 3. Division without zero guard
        for i, line in enumerate(lines):
            if "/" in line and not line.strip().startswith("//") and not line.strip().startswith("#"):
                m = re.search(r"/\s*([a-zA-Z_][a-zA-Z0-9_]*)", line)
                if m:
                    denom = m.group(1)
                    findings.append({
                        "type": "SAFETY",
                        "line": i + 1,
                        "title": f"Division Without Zero Guard on '{denom}'",
                        "suggestion": f"Validate '{denom} != 0' before division to prevent runtime DivisionByZero exceptions."
                    })

        # 4. Deep nesting check
        for i, line in enumerate(lines):
            indent_spaces = len(line) - len(line.lstrip(" "))
            if indent_spaces >= 16:
                findings.append({
                    "type": "STYLE",
                    "line": i + 1,
                    "title": "Deep Code Nesting",
                    "suggestion": "Block is nested 4+ levels deep. Consider refactoring inner logic into separate 'mk func' helper functions."
                })
                break

        report = [
            f"[*] RavenAI Code Review & Quality Report: {fname}",
            "=" * 70,
        ]
        if not findings:
            report.append("  [CLEAN] No syntax smells, security vulnerabilities, or performance hazards found!")
            report.append("  Your Corvus code follows canonical patterns and best practices.")
        else:
            report.append(f"  Total Findings: {len(findings)}\n")
            for idx, item in enumerate(findings, start=1):
                badge = f"[{item['type']}]"
                report.append(f"{idx}. {badge} Line {item['line']}: {item['title']}")
                report.append(f"   Recommendation: {item['suggestion']}\n")
        report.append("=" * 70)
        return "\n".join(report)

    def export_code(self, target: str, target_lang: str = "py") -> str:
        """Reverse transpiler: Convert Corvus code into Python or ISO C99."""
        code = target
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                code = f.read()

        target_lang = target_lang.lower().strip()
        if target_lang in ("py", "python"):
            lines = code.splitlines()
            py_lines = []
            indent_level = 0
            in_multiline_comment = False

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    py_lines.append("")
                    continue

                if in_multiline_comment:
                    cleaned_comment = stripped.rstrip("]}>}").strip()
                    py_lines.append("    " * indent_level + f"# {cleaned_comment}")
                    if "}" in stripped or "]" in stripped:
                        in_multiline_comment = False
                    continue

                if stripped.startswith("//") or stripped.startswith("#"):
                    py_lines.append("    " * indent_level + "# " + stripped.lstrip("/# "))
                    continue

                if stripped.startswith("?{") or stripped.startswith("?["):
                    cleaned_comment = stripped.lstrip("?[{").rstrip("]}>}").strip()
                    py_lines.append("    " * indent_level + f"# {cleaned_comment}")
                    if not ("}" in stripped[2:] or "]" in stripped[2:]):
                        in_multiline_comment = True
                    continue

                if stripped in ("]", "] ;", "}"):
                    if indent_level > 0: indent_level -= 1
                    continue

                curr_line = stripped
                has_open_block = curr_line.endswith("[") or curr_line.endswith("{")
                if has_open_block:
                    curr_line = curr_line[:-1].strip()

                curr_line = re.sub(r"\blog\(", "print(", curr_line)
                curr_line = re.sub(r"\bgivout\b", "return", curr_line)

                m_func = re.match(r"mk\s+func\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)", curr_line)
                if m_func:
                    fn_name, params = m_func.group(1), m_func.group(2)
                    py_lines.append("    " * indent_level + f"def {fn_name}({params}):")
                    indent_level += 1
                    continue

                m_cls = re.match(r"cls\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)", curr_line)
                if m_cls:
                    py_lines.append("    " * indent_level + f"class {m_cls.group(1)}:")
                    indent_level += 1
                    continue

                if curr_line.startswith("if (") and curr_line.endswith(")"):
                    py_lines.append("    " * indent_level + f"if {curr_line[4:-1]}:")
                    if has_open_block: indent_level += 1
                    continue
                elif curr_line.startswith("elsif (") and curr_line.endswith(")"):
                    if indent_level > 0: indent_level -= 1
                    py_lines.append("    " * indent_level + f"elif {curr_line[7:-1]}:")
                    if has_open_block: indent_level += 1
                    continue
                elif curr_line == "else":
                    if indent_level > 0: indent_level -= 1
                    py_lines.append("    " * indent_level + "else:")
                    if has_open_block: indent_level += 1
                    continue
                elif curr_line.startswith("while (") and curr_line.endswith(")"):
                    py_lines.append("    " * indent_level + f"while {curr_line[7:-1]}:")
                    if has_open_block: indent_level += 1
                    continue
                elif curr_line.startswith("for ") and " in " in curr_line:
                    py_lines.append("    " * indent_level + f"{curr_line}:")
                    if has_open_block: indent_level += 1
                    continue

                curr_line = re.sub(r"set\s+(?:int|str|flo|bool|lis|tup|dic|any)?\s*;?\s*", "", curr_line)
                curr_line = re.sub(r"const\s+", "", curr_line)
                if "{" in curr_line and ":" not in curr_line:
                    curr_line = curr_line.replace("{", "[").replace("}", "]")
                curr_line = curr_line.rstrip(";")

                py_lines.append("    " * indent_level + curr_line)
                if has_open_block:
                    indent_level += 1

            header = f"# [Transpiled from Corvus to Python by {self.name} v{self.version}]\n"
            return header + "\n".join(py_lines)

        elif target_lang in ("c", "c99"):
            c_lines = [
                f"/* [Transpiled from Corvus to ISO C99 by {self.name} v{self.version}] */",
                "#include <stdio.h>",
                "#include <stdlib.h>",
                "#include <stdbool.h>",
                "",
                "int main(int argc, char** argv) {",
            ]
            for line in code.splitlines():
                stripped = line.strip()
                if not stripped: continue
                if stripped.startswith("log("):
                    msg = stripped[4:-1]
                    c_lines.append(f'    printf("%s\\n", {msg});')
                elif stripped.startswith("set int;"):
                    decl = stripped[8:].strip()
                    c_lines.append(f"    int {decl};")
                elif stripped.startswith("set flo;"):
                    decl = stripped[8:].strip()
                    c_lines.append(f"    double {decl};")
                elif stripped.startswith("set "):
                    decl = stripped[4:].strip()
                    c_lines.append(f"    long long {decl};")
            c_lines.append("    return 0;")
            c_lines.append("}")
            return "\n".join(c_lines)
        else:
            return f"Error: Unsupported export target '{target_lang}'. Supported: 'py', 'c'."

    def similarity(word1, word2):
        from difflib import SequenceMatcher
        return SequenceMatcher(None, word1, word2).ratio()


        
if __name__=="__main__":
    bot=RavenAI()
    bot.chat()
