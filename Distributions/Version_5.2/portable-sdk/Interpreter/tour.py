"""Corvus Interactive Tour Engine (corvus tour)
Interactive in-terminal guided tutorial inspired by vimtutor and rustlings.
"""

import sys
import os

LESSONS = [
    {
        "id": 1,
        "title": "Hello World & Output with log()",
        "description": (
            "In Corvus, printing output to the console is done using the 'log(...)' function.\n"
            "Unlike Python's 'print', Corvus uses 'log' across all versions."
        ),
        "example": 'log("Hello, Corvus!")',
        "task": 'Write a Corvus expression to log "Welcome to the Tour!" to the screen.',
        "validator": lambda code, stdout: "Welcome to the Tour!" in stdout,
        "hint": 'Type: log("Welcome to the Tour!")',
        "solution": 'log("Welcome to the Tour!")'
    },
    {
        "id": 2,
        "title": "Variables & Auto Type Inference",
        "description": (
            "Corvus uses 'set' to declare variables. In modern Corvus (v4.4+),\n"
            "types can be inferred automatically (set x = 10) or declared explicitly\n"
            "(set int; x = 10). Constants are defined with 'const PI = 3.14159'."
        ),
        "example": "set message = \"Corvus is fast\"\nconst MAX = 100\nlog(message, MAX)",
        "task": "Declare a variable 'score' equal to 95 and log its value.",
        "validator": lambda code, stdout: "95" in stdout,
        "hint": "Type: set score = 95\nlog(score)",
        "solution": "set score = 95\nlog(score)"
    },
    {
        "id": 3,
        "title": "Functions & Return Values with givout",
        "description": (
            "Functions in Corvus are defined with 'mk func name(params) [ ... ]'.\n"
            "To return a value, Corvus uses the dedicated keyword 'givout'."
        ),
        "example": "mk func square(n) [\n    givout n * n\n]\nlog(square(5))",
        "task": "Write a function 'double_val(n)' that returns n * 2, then log double_val(21).",
        "validator": lambda code, stdout: "42" in stdout,
        "hint": "mk func double_val(n) [ givout n * 2 ]\nlog(double_val(21))",
        "solution": "mk func double_val(n) [\n    givout n * 2\n]\nlog(double_val(21))"
    },
    {
        "id": 4,
        "title": "Block Scoping [ ... ] and Lists { ... }",
        "description": (
            "Corvus uniquely uses square brackets [ ... ] for code blocks\n"
            "and curly braces { ... } for native list collections."
        ),
        "example": "set lis; numbers = {1, 2, 3}\nif (numbers.len() > 0) [\n    log(numbers[0])\n]",
        "task": "Create a list 'fruits' containing {\"apple\", \"banana\"} and log the first item.",
        "validator": lambda code, stdout: "apple" in stdout,
        "hint": 'set fruits = {"apple", "banana"}\nlog(fruits[0])',
        "solution": 'set fruits = {"apple", "banana"}\nlog(fruits[0])'
    },
    {
        "id": 5,
        "title": "Object-Oriented Classes & self.",
        "description": (
            "Classes are declared with 'cls Name() [ ... ]'.\n"
            "Constructors are named 'init', and methods reference instance attributes with 'self.'."
        ),
        "example": (
            "cls Hero() [\n"
            "    set str; name\n"
            "    mk func init(n) [ self.name = n ]\n"
            "    mk func greet() [ log(\"Hero:\", self.name) ]\n"
            "]\n"
            "set h = Hero(\"Saatvik\")\n"
            "h.greet()"
        ),
        "task": "Declare a class 'Box()' with an init(val) saving self.val, and log a Box(777).val.",
        "validator": lambda code, stdout: "777" in stdout,
        "hint": "cls Box() [ set val\n mk func init(v) [ self.val = v ] ]\nset b = Box(777)\nlog(b.val)",
        "solution": "cls Box() [\n    set any; val\n    mk func init(v) [\n        self.val = v\n    ]\n]\nset b = Box(777)\nlog(b.val)"
    },
    {
        "id": 6,
        "title": "Native Matrix Multiplication Operator (@)",
        "description": (
            "Corvus features a native '@' operator for matrix multiplication\n"
            "on 2D collections, NumPy arrays, and PyTorch tensors."
        ),
        "example": "set A = [[1, 2], [3, 4]]\nset B = [[5, 6], [7, 8]]\nlog(A @ B)",
        "task": "Multiply 2D matrices [[2, 0], [0, 2]] @ [[3, 4], [5, 6]] and log the result.",
        "validator": lambda code, stdout: "6" in stdout and "12" in stdout,
        "hint": "set A = [[2, 0], [0, 2]]\nset B = [[3, 4], [5, 6]]\nlog(A @ B)",
        "solution": "set A = [[2, 0], [0, 2]]\nset B = [[3, 4], [5, 6]]\nlog(A @ B)"
    },
    {
        "id": 7,
        "title": "Concurrency with 'Murder of Crows'",
        "description": (
            "Corvus provides high-speed concurrency via the 'crow' engine.\n"
            "Spawn background parallel tasks with 'crow.spawn' or 'crow.parallel_map'."
        ),
        "example": "get crow\nset task = crow.spawn(func() [ log(\"In background\") ])\ncrow.join(task)",
        "task": "Import crow using 'get crow' and log crow.status or spawn a task.",
        "validator": lambda code, stdout: True,
        "hint": "get crow\nlog(\"Crow Engine Ready\")",
        "solution": "get crow\nlog(\"Crow Engine Ready\")"
    },
    {
        "id": 8,
        "title": "Structured Error Resilience with try ... error ... final",
        "description": (
            "Corvus replaces traditional try-catch with 'try [ ... ] error(err) [ ... ] final [ ... ]'.\n"
            "The error block receives an error dictionary with 'message' and 'type'."
        ),
        "example": "try [\n    set x = 10 / 0\n] error(e) [\n    log(\"Caught safely:\", e[\"message\"])\n] final [\n    log(\"Done\")\n]",
        "task": "Write a try/error block that catches an intentional error and logs 'Recovered'.",
        "validator": lambda code, stdout: "Recovered" in stdout,
        "hint": "try [ set x = 1 / 0 ] error(e) [ log(\"Recovered\") ]",
        "solution": "try [\n    set x = 1 / 0\n] error(e) [\n    log(\"Recovered\")\n]"
    }
]

def run_code_capture(code: str):
    """Execute Corvus code and capture standard output."""
    import io
    from lexercorvus import tokenize
    from parsercorvus import Parser
    from evaluatorcorvus import Evaluator, Environment

    old_stdout = sys.stdout
    redirected = io.StringIO()
    sys.stdout = redirected
    err_msg = None
    try:
        tokens = tokenize(code)
        ast = Parser(tokens).parse()
        evaluator = Evaluator(Environment())
        evaluator.evaluate(ast)
    except Exception as e:
        err_msg = str(e)
    finally:
        sys.stdout = old_stdout

    return redirected.getvalue(), err_msg

def start_tour():
    """Launch the interactive Corvus Tour CLI."""
    print("=" * 70)
    print("   🐦 Welcome to the Interactive Corvus Language Tour (corvus tour)   ")
    print("=" * 70)
    print("Learn Corvus hands-on! Type your code, test solutions, and master the syntax.")
    print("Special Commands:")
    print("  'run'    - Execute the code you have entered")
    print("  'hint'   - Display a hint for the current lesson")
    print("  'sol'    - Reveal the reference solution")
    print("  'skip'   - Skip to the next lesson")
    print("  'exit'   - Exit the tour")
    print("=" * 70)

    for lesson in LESSONS:
        print(f"\n--- Lesson {lesson['id']}/{len(LESSONS)}: {lesson['title']} ---")
        print(lesson["description"])
        print("\nReference Example:")
        for line in lesson["example"].splitlines():
            print(f"  {line}")
        print(f"\nYour Task: {lesson['task']}")

        buffer = []
        while True:
            try:
                line = input("corvus-tour > ")
            except (EOFError, KeyboardInterrupt):
                print("\nTour exited. Come back anytime!")
                return

            cmd = line.strip().lower()
            if cmd == "exit" or cmd == "quit":
                print("Tour exited. Keep coding in Corvus!")
                return
            elif cmd == "hint":
                print(f"[Hint]: {lesson['hint']}")
                continue
            elif cmd == "sol":
                print(f"[Reference Solution]:\n{lesson['solution']}")
                continue
            elif cmd == "skip":
                print("[!] Lesson skipped.")
                break
            elif cmd == "run" or (line.strip() and not buffer and ";" in line or "log(" in line):
                # If 'run' was typed or immediate one-liner
                code_to_test = "\n".join(buffer) if cmd == "run" else line
                if not code_to_test.strip():
                    print("Please enter code first before typing 'run'.")
                    continue

                stdout_text, err = run_code_capture(code_to_test)
                if err:
                    print(f"[Execution Error]: {err}")
                    print("Try again or type 'hint' for help.")
                    buffer = []
                    continue

                print("[Output]:")
                for out_line in stdout_text.splitlines():
                    print(f"  {out_line}")

                if lesson["validator"](code_to_test, stdout_text):
                    print(f"\n[SUCCESS] Excellent! Lesson {lesson['id']} completed!\n")
                    break
                else:
                    print("[!] Output did not satisfy the task criteria. Try again or type 'hint'.")
                    buffer = []
            else:
                buffer.append(line)

    print("\n" + "=" * 70)
    print("🎉 CONGRATULATIONS! You have completed the Corvus Language Tour!")
    print("You now know variables, functions, scoping, OOP, matrix math, concurrency, and error handling.")
    print("=" * 70)

def verify_all_lessons_smoke():
    """Headless verification check testing all reference solutions."""
    for lesson in LESSONS:
        sol = lesson["solution"]
        stdout, err = run_code_capture(sol)
        if err:
            raise RuntimeError(f"Tour Lesson {lesson['id']} solution failed with error: {err}")
        if not lesson["validator"](sol, stdout):
            raise RuntimeError(f"Tour Lesson {lesson['id']} solution output did not pass validator!")
    return True
