import re
import os
import time
from difflib import SequenceMatcher
class RavenAI:
    def __init__(self):
        self.name="RavenAI"
        self.version="1.0"
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
        print("  Commands: 'code--ask' | 'code--summary' | 'code--fix' | 'code--translate' | 'exit'")
        print("=" * 60)
        while True:
            user_prompt=input("\nRavenAI  >")
            if "code--summary" == user_prompt:
                path=input("Please state the path of the file:")
                time.sleep(2)
                print("\n"+self.explain(path))
            elif "code--ask"== user_prompt:
                question=input("Please state your Corvus question:")
                time.sleep(2)
                print(self.ask("\n"+question))
            elif "code--fix" == user_prompt:
                target = input("Please enter code snippet or file path to fix: ")
                time.sleep(2)
                print("\n" + self.fix(target))
            elif "code--translate" == user_prompt:
                target = input("Please enter Python snippet or file path to translate: ")
                time.sleep(2)
                print("\n" + self.translate(target))
            elif "exit" == user_prompt:
                time.sleep(2)
                print("RavenAI chat mode exited.")
                break
            else:
                print("Unknown command. Please type 'code--ask', 'code--summary', 'code--fix', 'code--translate', or 'exit'.")

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

    def similarity(word1, word2):
        from difflib import SequenceMatcher
        return SequenceMatcher(None, word1, word2).ratio()


        
if __name__=="__main__":
    bot=RavenAI()
    bot.chat()
