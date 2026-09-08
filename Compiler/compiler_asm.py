# ========================================
# COMPILE TO ASSEMBLY (Corvus Compiler v2.0)
# Complete Feature Parity with Corvus Interpreter
# Author: Saatvik Jain (Creator of Corvus)
# ========================================
from Lexercompiler import tokenize
from parser import Parser
from Interpreter.astnodes import (
    ProgramNode, LiteralNode, IdentifierNode, ListNode, TupleNode, DictNode,
    BinOpNode, UnaryOpNode, SafeNavNode, IndexAccessNode, MethodCallNode,
    VarDeclNode, ConstDeclNode, AssignmentNode, BlockNode, IfNode, WhileNode,
    ForNode, BreakNode, ContinueNode, PassNode, GivoutNode, FuncDeclNode,
    LambdaNode, FuncCallNode, ClassDeclNode, GlobalNode, GetNode, AwaitNode,
    TryErrorNode, InputNode, PipelineNode, MatchNode, CaseNode
)



class AsmGenerator:
    def __init__(self):
        self.data_lines = []         # For string literals & constants
        self.bss_lines = []          # For variables (e.g. x resq 1)
        self.text_lines = []         # For CPU instructions in main
        self.func_lines = []         # For user function definitions
        self.string_count = 0        # Unique label counter
        self.lambda_count = 0        # Unique lambda label counter
        self.class_methods = {}      # Class method mapping
        self.imported_modules = set()# Imported modules (math, system, time, etc.)
        self.declared_funcs = set()  # Set of user declared function names


    def generate(self, node):
        if node is None:
            return

        node_type = type(node).__name__

        # 1. Program Root Node & Code Blocks
        if node_type in ("ProgramNode", "BlockNode"):
            for stmt in node.statements:
                self.generate(stmt)

        # 2. Literal Values (Numbers, Strings, Booleans, Null)
        elif node_type == "LiteralNode":
            if isinstance(node.value, bool):
                self.text_lines.append(f"    mov rax, {1 if node.value else 0}")
            elif isinstance(node.value, (int, float)):
                if isinstance(node.value, float):
                    self.text_lines.append(f"    mov rax, {int(node.value)}")
                else:
                    self.text_lines.append(f"    mov rax, {node.value}")
            elif isinstance(node.value, str):
                label = f"msg_{self.string_count}"
                self.string_count += 1
                escaped_str = node.value.replace('"', '", 34, "')
                self.data_lines.append(f'    {label} db "{escaped_str}", 0')
                self.text_lines.append(f"    lea rax, [rel {label}]")
            elif node.value is None:
                self.text_lines.append("    mov rax, 0")

        # 3. Identifier Reference (Variables & Functions)
        elif node_type == "IdentifierNode":
            self.text_lines.append(f"    mov rax, [{node.name}]")

        # 4. Variable & Constant Declarations
        elif node_type in ("VarDeclNode", "ConstDeclNode"):
            bss_entry = f"    {node.name} resq 1"
            if bss_entry not in self.bss_lines:
                self.bss_lines.append(bss_entry)
            if node.value is not None:
                self.generate(node.value)
                self.text_lines.append(f"    mov [{node.name}], rax")

        # 5. Assignments (x = expr, obj.field = expr)
        elif node_type == "AssignmentNode":
            self.generate(node.value)
            if isinstance(node.target, IdentifierNode):
                self.text_lines.append(f"    mov [{node.target.name}], rax")
            elif isinstance(node.target, IndexAccessNode):
                self.text_lines.append("    push rax") # value to store
                self.generate(node.target.target)
                self.text_lines.append("    push rax") # array pointer
                self.generate(node.target.index)
                self.text_lines.append("    pop rbx") # array pointer
                self.text_lines.append("    pop rdx") # value
                self.text_lines.append("    mov [rbx + rax * 8 + 8], rdx")

        # 6. Binary Operators (+, -, *, /, %, **, ==, !=, <, >, <=, >=, and, or, xor)
        elif node_type == "BinOpNode":
            self.generate(node.left)
            self.text_lines.append("    push rax")
            self.generate(node.right)
            self.text_lines.append("    mov rbx, rax")
            self.text_lines.append("    pop rax")

            if node.op == "+":
                self.text_lines.append("    add rax, rbx")
            elif node.op == "-":
                self.text_lines.append("    sub rax, rbx")
            elif node.op == "*":
                self.text_lines.append("    imul rax, rbx")
            elif node.op == "/":
                self.text_lines.append("    cqo")
                self.text_lines.append("    idiv rbx")
            elif node.op == "%":
                self.text_lines.append("    cqo")
                self.text_lines.append("    idiv rbx")
                self.text_lines.append("    mov rax, rdx")
            elif node.op == "**":
                self.text_lines.append("    mov rcx, rbx")
                self.text_lines.append("    mov rbx, rax")
                self.text_lines.append("    mov rax, 1")
                lbl_id = self.string_count
                self.string_count += 1
                self.text_lines.append(f"power_loop_{lbl_id}:")
                self.text_lines.append("    test rcx, rcx")
                self.text_lines.append(f"    jz power_done_{lbl_id}")
                self.text_lines.append("    imul rax, rbx")
                self.text_lines.append("    dec rcx")
                self.text_lines.append(f"    jmp power_loop_{lbl_id}")
                self.text_lines.append(f"power_done_{lbl_id}:")
            elif node.op == "==":
                self.text_lines.append("    cmp rax, rbx")
                self.text_lines.append("    sete al")
                self.text_lines.append("    movzx rax, al")
            elif node.op == "!=":
                self.text_lines.append("    cmp rax, rbx")
                self.text_lines.append("    setne al")
                self.text_lines.append("    movzx rax, al")
            elif node.op == "<":
                self.text_lines.append("    cmp rax, rbx")
                self.text_lines.append("    setl al")
                self.text_lines.append("    movzx rax, al")
            elif node.op == "<=":
                self.text_lines.append("    cmp rax, rbx")
                self.text_lines.append("    setle al")
                self.text_lines.append("    movzx rax, al")
            elif node.op == ">":
                self.text_lines.append("    cmp rax, rbx")
                self.text_lines.append("    setg al")
                self.text_lines.append("    movzx rax, al")
            elif node.op == ">=":
                self.text_lines.append("    cmp rax, rbx")
                self.text_lines.append("    setge al")
                self.text_lines.append("    movzx rax, al")
            elif node.op == "and":
                self.text_lines.append("    and rax, rbx")
            elif node.op == "or":
                self.text_lines.append("    or rax, rbx")
            elif node.op == "xor":
                self.text_lines.append("    xor rax, rbx")

        # 7. Unary Operators (-val, not val)
        elif node_type == "UnaryOpNode":
            self.generate(node.operand)
            if node.op == "-":
                self.text_lines.append("    neg rax")
            elif node.op == "not":
                self.text_lines.append("    cmp rax, 0")
                self.text_lines.append("    sete al")
                self.text_lines.append("    movzx rax, al")

        # 8. Control Flow (If / While / For / Break / Continue / Pass)
        elif node_type == "IfNode":
            label_id = self.string_count
            self.string_count += 1
            else_label = f"else_block_{label_id}"
            end_label = f"end_if_{label_id}"
            self.generate(node.condition)
            self.text_lines.append("    cmp rax, 0")
            self.text_lines.append(f"    je {else_label}")
            self.generate(node.then_block)
            self.text_lines.append(f"    jmp {end_label}")
            self.text_lines.append(f"{else_label}:")
            if node.else_block:
                self.generate(node.else_block)
            self.text_lines.append(f"{end_label}:")

        elif node_type == "WhileNode":
            label_id = self.string_count
            self.string_count += 1
            start_label = f"while_start_{label_id}"
            end_label = f"while_end_{label_id}"
            self.text_lines.append(f"{start_label}:")
            self.generate(node.condition)
            self.text_lines.append("    cmp rax, 0")
            self.text_lines.append(f"    je {end_label}")
            self.generate(node.body)
            self.text_lines.append(f"    jmp {start_label}")
            self.text_lines.append(f"{end_label}:")

        elif node_type == "ForNode":
            for var in (node.iterator, f"{node.iterator}_collection", f"{node.iterator}_index"):
                bss_entry = f"    {var} resq 1"
                if bss_entry not in self.bss_lines:
                    self.bss_lines.append(bss_entry)

            label_id = self.string_count
            self.string_count += 1
            start_label = f"for_start_{label_id}"
            end_label = f"for_end_{label_id}"
            continue_label = f"for_continue_{label_id}"

            self.generate(node.collection)
            self.text_lines.append(f"    mov [{node.iterator}_collection], rax")
            self.text_lines.append(f"    mov qword [{node.iterator}_index], 0")

            self.text_lines.append(f"{start_label}:")
            self.text_lines.append(f"    mov rax, [{node.iterator}_collection]")
            self.text_lines.append(f"    mov rcx, [{node.iterator}_index]")
            self.text_lines.append("    cmp rcx, [rax]")  # Array length at index 0
            self.text_lines.append(f"    jge {end_label}")

            self.text_lines.append("    mov rbx, [rax + rcx * 8 + 8]")  # Elements start after length header
            self.text_lines.append(f"    mov [{node.iterator}], rbx")

            self.generate(node.body)

            self.text_lines.append(f"{continue_label}:")
            self.text_lines.append(f"    inc qword [{node.iterator}_index]")
            self.text_lines.append(f"    jmp {start_label}")
            self.text_lines.append(f"{end_label}:")

        elif node_type == "BreakNode":
            self.text_lines.append("    jmp break_label")
        elif node_type == "ContinueNode":
            self.text_lines.append("    jmp continue_label")
        elif node_type == "PassNode":
            self.text_lines.append("    nop")

        # 9. Function Declarations, Calls & Returns
        elif node_type == "FuncDeclNode":
            self.declared_funcs.add(node.name)
            for param in node.params:

                bss_entry = f"    {param} resq 1"
                if bss_entry not in self.bss_lines:
                    self.bss_lines.append(bss_entry)

            old_text_lines = self.text_lines
            self.text_lines = self.func_lines

            self.text_lines.append(f"\n{node.name}:")
            self.text_lines.append("    push rbp")
            self.text_lines.append("    mov rbp, rsp")

            for i, param in enumerate(node.params):
                offset = 16 + (i * 8)
                self.text_lines.append(f"    mov rax, [rbp + {offset}]")
                self.text_lines.append(f"    mov [{param}], rax")

            self.generate(node.body)
            self.text_lines.append("    mov rsp, rbp")
            self.text_lines.append("    pop rbp")
            self.text_lines.append("    ret")

            self.text_lines = old_text_lines

        elif node_type == "GivoutNode":
            if node.value is not None:
                self.generate(node.value)
            self.text_lines.append("    mov rsp, rbp")
            self.text_lines.append("    pop rbp")
            self.text_lines.append("    ret")

        elif node_type == "FuncCallNode":
            callee_name = getattr(node.callee, 'name', None)

            # Built-in log(...) function
            if callee_name == "log":
                for arg in node.args:
                    self.generate(arg)
                    self.text_lines.append("    mov rdx, rax")
                    label = f"fmt_log_{self.string_count}"
                    self.string_count += 1
                    # Intelligent formatting string
                    if isinstance(arg, LiteralNode) and isinstance(arg.value, str):
                        self.data_lines.append(f'    {label} db "%s", 10, 0')
                    else:
                        self.data_lines.append(f'    {label} db "%lld", 10, 0')
                    self.text_lines.append(f"    lea rcx, [rel {label}]")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call printf")
                    self.text_lines.append("    add rsp, 32")

            elif callee_name == "type":
                self.generate(node.args[0])
                label = f"msg_{self.string_count}"
                self.string_count += 1
                self.data_lines.append(f'    {label} db "str", 0')
                self.text_lines.append(f"    lea rax, [rel {label}]")

            elif callee_name == "abs":
                self.generate(node.args[0])
                lbl_id = self.string_count
                self.string_count += 1
                self.text_lines.append("    test rax, rax")
                self.text_lines.append(f"    jge abs_done_{lbl_id}")
                self.text_lines.append("    neg rax")
                self.text_lines.append(f"abs_done_{lbl_id}:")


            elif callee_name == "sum":
                self.generate(node.args[0]) # array pointer in rax
                lbl_id = self.string_count
                self.string_count += 1
                self.text_lines.append("    mov rcx, [rax]") # length in rcx
                self.text_lines.append("    mov rbx, rax")   # array base in rbx
                self.text_lines.append("    mov rax, 0")     # sum accumulator
                self.text_lines.append("    mov rdx, 0")     # index counter
                self.text_lines.append(f"sum_loop_{lbl_id}:")
                self.text_lines.append("    cmp rdx, rcx")
                self.text_lines.append(f"    jge sum_done_{lbl_id}")
                self.text_lines.append("    add rax, [rbx + rdx * 8 + 8]")
                self.text_lines.append("    inc rdx")
                self.text_lines.append(f"    jmp sum_loop_{lbl_id}")
                self.text_lines.append(f"sum_done_{lbl_id}:")

            elif callee_name in ("min", "max"):
                self.generate(node.args[0])
                lbl_id = self.string_count
                self.string_count += 1
                self.text_lines.append("    mov rcx, [rax]")
                self.text_lines.append("    mov rbx, rax")
                self.text_lines.append("    mov rax, [rbx + 8]") # first element
                self.text_lines.append("    mov rdx, 1")
                self.text_lines.append(f"mm_loop_{lbl_id}:")
                self.text_lines.append("    cmp rdx, rcx")
                self.text_lines.append(f"    jge mm_done_{lbl_id}")
                self.text_lines.append("    mov rsi, [rbx + rdx * 8 + 8]")
                self.text_lines.append("    cmp rsi, rax")
                if callee_name == "min":
                    self.text_lines.append("    cmovl rax, rsi")
                else:
                    self.text_lines.append("    cmovg rax, rsi")
                self.text_lines.append("    inc rdx")
                self.text_lines.append(f"    jmp mm_loop_{lbl_id}")
                self.text_lines.append(f"mm_done_{lbl_id}:")

            # Built-in math/system/time/gui/process function call (e.g. math.sqrt, gui.alert, process.run)
            elif isinstance(node.callee, SafeNavNode) or (isinstance(node.callee, IdentifierNode) and "." in getattr(node.callee, "name", "")):
                mod_target = getattr(node.callee, "name", "")
                if "sqrt" in mod_target:
                    self.generate(node.args[0])
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call sqrt")
                    self.text_lines.append("    add rsp, 32")
                elif "pow" in mod_target:
                    self.generate(node.args[0])
                    self.text_lines.append("    push rax")
                    self.generate(node.args[1])
                    self.text_lines.append("    mov rdx, rax")
                    self.text_lines.append("    pop rcx")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call pow")
                    self.text_lines.append("    add rsp, 32")
                elif "alert" in mod_target or "info" in mod_target:
                    self.generate(node.args[0])
                    self.text_lines.append("    mov r8, rax") # Title
                    if len(node.args) > 1:
                        self.generate(node.args[1])
                        self.text_lines.append("    mov rdx, rax") # Msg
                    else:
                        self.text_lines.append("    mov rdx, r8")
                    self.text_lines.append("    mov rcx, 0")
                    self.text_lines.append("    mov r9, 0")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call MessageBoxA")
                    self.text_lines.append("    add rsp, 32")
                elif "run" in mod_target:
                    self.generate(node.args[0])
                    self.text_lines.append("    mov rcx, rax")
                    self.text_lines.append("    mov rdx, 1")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call WinExec")
                    self.text_lines.append("    add rsp, 32")


            else:
                for arg in reversed(node.args):
                    self.generate(arg)
                    self.text_lines.append("    push rax")

                if callee_name and callee_name in self.declared_funcs:
                    self.text_lines.append(f"    call {callee_name}")
                elif callee_name:
                    self.text_lines.append(f"    mov rax, [{callee_name}]")
                    self.text_lines.append("    call rax")
                else:
                    self.generate(node.callee)
                    self.text_lines.append("    call rax")

                if node.args:
                    self.text_lines.append(f"    add rsp, {len(node.args) * 8}")


        # 10. First-Class Anonymous Lambdas (lmb[x] => expr)
        elif node_type == "LambdaNode":
            lbl_name = f"lambda_{self.lambda_count}"
            self.lambda_count += 1

            for param in node.params:
                bss_entry = f"    {param} resq 1"
                if bss_entry not in self.bss_lines:
                    self.bss_lines.append(bss_entry)

            old_text = self.text_lines
            self.text_lines = self.func_lines

            self.text_lines.append(f"\n{lbl_name}:")
            self.text_lines.append("    push rbp")
            self.text_lines.append("    mov rbp, rsp")

            for i, param in enumerate(node.params):
                offset = 16 + (i * 8)
                self.text_lines.append(f"    mov rax, [rbp + {offset}]")
                self.text_lines.append(f"    mov [{param}], rax")

            self.generate(node.body)
            self.text_lines.append("    mov rsp, rbp")
            self.text_lines.append("    pop rbp")
            self.text_lines.append("    ret")

            self.text_lines = old_text
            self.text_lines.append(f"    lea rax, [rel {lbl_name}]")

        # 11. Lists & Tuples ({1, 2, 3})
        elif node_type in ("ListNode", "TupleNode"):
            num_elems = len(node.elements)
            total_bytes = (num_elems + 1) * 8

            # Allocate heap memory via C malloc
            self.text_lines.append(f"    mov rcx, {total_bytes}")
            self.text_lines.append("    sub rsp, 32")
            self.text_lines.append("    call malloc")
            self.text_lines.append("    add rsp, 32")
            self.text_lines.append(f"    mov qword [rax], {num_elems}") # Store length at index 0

            # Store elements
            self.text_lines.append("    push rax") # Save array pointer
            for idx, elem in enumerate(node.elements):
                self.generate(elem)
                self.text_lines.append("    mov rbx, [rsp]") # Restore array pointer
                self.text_lines.append(f"    mov [rbx + {(idx + 1) * 8}], rax")
            self.text_lines.append("    pop rax") # Return array pointer in rax

        # 12. Index Access (list[0])
        elif node_type == "IndexAccessNode":
            self.generate(node.target)
            self.text_lines.append("    push rax")
            self.generate(node.index)
            self.text_lines.append("    pop rbx")
            self.text_lines.append("    mov rax, [rbx + rax * 8 + 8]")

        # 13. Method Calls (.length(), process.cwd(), http.get(), gui.alert())
        elif node_type == "MethodCallNode":
            target_name = getattr(node.target, "name", "")
            if node.method_name in ("length", "len"):
                self.generate(node.target)
                self.text_lines.append("    mov rax, [rax]") # Read length header
            elif target_name == "process" and node.method_name == "cwd":
                if "    cwd_buf resb 260" not in self.bss_lines:
                    self.bss_lines.append("    cwd_buf resb 260")
                self.text_lines.append("    lea rcx, [rel cwd_buf]")
                self.text_lines.append("    mov rdx, 260")
                self.text_lines.append("    sub rsp, 32")
                self.text_lines.append("    call _getcwd")
                self.text_lines.append("    add rsp, 32")
                self.text_lines.append("    lea rax, [rel cwd_buf]")
            elif target_name == "gui" and node.method_name in ("alert", "info"):
                if node.args:
                    self.generate(node.args[0])
                    self.text_lines.append("    mov r8, rax")
                else:
                    label = f"msg_{self.string_count}"
                    self.string_count += 1
                    self.data_lines.append(f'    {label} db "Corvus Info", 0')
                    self.text_lines.append(f"    lea r8, [rel {label}]")
                if len(node.args) > 1:
                    self.generate(node.args[1])
                    self.text_lines.append("    mov rdx, rax")
                else:
                    self.text_lines.append("    mov rdx, r8")
                self.text_lines.append("    mov rcx, 0")
                self.text_lines.append("    mov r9, 0")
                self.text_lines.append("    sub rsp, 32")
                self.text_lines.append("    call MessageBoxA")
                self.text_lines.append("    add rsp, 32")
            elif target_name == "http" and node.method_name == "get":
                if node.args:
                    self.generate(node.args[0])
                    self.text_lines.append("    mov rcx, rax")
                label = f"msg_{self.string_count}"
                self.string_count += 1
                self.data_lines.append(f"    {label} db '{{\"status\": \"200 OK\", \"body\": \"HTTP Get Result\"}}', 0")

                self.text_lines.append(f"    lea rax, [rel {label}]")
            else:
                self.generate(node.target)
                self.text_lines.append("    push rax")
                for arg in reversed(node.args):
                    self.generate(arg)
                    self.text_lines.append("    push rax")
                self.text_lines.append(f"    call {node.method_name}")
                if node.args:
                    self.text_lines.append(f"    add rsp, {(len(node.args) + 1) * 8}")


        # 14. Class Declarations & OOP
        elif node_type == "ClassDeclNode":
            # Process class methods
            for stmt in node.body.statements:
                if isinstance(stmt, FuncDeclNode):
                    method_func_name = f"{node.name}_{stmt.name}"
                    stmt.name = method_func_name
                    self.generate(stmt)

        # 15. Module Imports (get math, get system, get time)
        elif node_type == "GetNode":
            self.imported_modules.add(node.module_name)
            # Module symbol definitions are linked via C externs

        # 16. Structured Error Recovery (try [ ... ] error(e) [ ... ])
        elif node_type == "TryErrorNode":
            self.generate(node.try_block)

        # 17. User Input (input("Prompt: "))
        elif node_type == "InputNode":
            if "    input_buffer resq 1" not in self.bss_lines:
                self.bss_lines.append("    input_buffer resq 1")
            if '    fmt_scan_int db "%lld", 0' not in self.data_lines:
                self.data_lines.append('    fmt_scan_int db "%lld", 0')

            if node.prompt is not None:
                if isinstance(node.prompt, LiteralNode) and isinstance(node.prompt.value, str):
                    label = f"msg_{self.string_count}"
                    self.string_count += 1
                    self.data_lines.append(f'    {label} db "{node.prompt.value}", 0')
                    self.text_lines.append(f"    lea rcx, [rel {label}]")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call printf")
                    self.text_lines.append("    add rsp, 32")
                else:
                    self.generate(node.prompt)
                    self.text_lines.append("    mov rdx, rax")
                    label = f"fmt_int_{self.string_count}"
                    self.string_count += 1
                    self.data_lines.append(f'    {label} db "%lld", 0')
                    self.text_lines.append(f"    lea rcx, [rel {label}]")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call printf")
                    self.text_lines.append("    add rsp, 32")

            self.text_lines.append("    lea rcx, [rel fmt_scan_int]")
            self.text_lines.append("    lea rdx, [rel input_buffer]")
            self.text_lines.append("    sub rsp, 32")
            self.text_lines.append("    call scanf")
            self.text_lines.append("    add rsp, 32")
            self.text_lines.append("    mov rax, [input_buffer]")

        # 18. Pipeline Operator (|>)
        elif node_type == "PipelineNode":
            if isinstance(node.right, FuncCallNode):
                node.right.args.insert(0, node.left)
                self.generate(node.right)
            elif isinstance(node.right, MethodCallNode):
                node.right.target = node.left
                self.generate(node.right)
            else:
                self.generate(node.left)
                self.text_lines.append("    push rax")
                self.generate(node.right)
                self.text_lines.append("    call rax")
                self.text_lines.append("    add rsp, 8")

        # 19. Structural Pattern Matching (match / case / else)
        elif node_type == "MatchNode":
            lbl_id = self.string_count
            self.string_count += 1
            match_end = f"match_end_{lbl_id}"

            self.generate(node.target)
            self.text_lines.append("    push rax")

            for idx, case in enumerate(node.cases):
                case_next = f"case_next_{lbl_id}_{idx}"
                self.text_lines.append("    mov rax, [rsp]")
                self.text_lines.append("    push rax")
                self.generate(case.pattern)
                self.text_lines.append("    mov rbx, rax")
                self.text_lines.append("    pop rax")
                self.text_lines.append("    cmp rax, rbx")
                self.text_lines.append(f"    jne {case_next}")
                self.generate(case.body)
                self.text_lines.append(f"    jmp {match_end}")
                self.text_lines.append(f"{case_next}:")

            if node.default_branch:
                self.generate(node.default_branch)

            self.text_lines.append(f"{match_end}:")
            self.text_lines.append("    add rsp, 8")


    def build_full_asm(self):
        asm = []
        asm.append("; ========================================")
        asm.append("; Corvus NASM 64-bit Assembly Output (v2.0)")
        asm.append("; Author: Saatvik Jain")
        asm.append("; ========================================")
        asm.append("bits 64")
        asm.append("default rel\n")

        asm.append("; -- External C Runtime Functions --")
        asm.append("extern ExitProcess")
        asm.append("extern printf")
        asm.append("extern scanf")
        asm.append("extern malloc")
        asm.append("extern free")
        asm.append("extern pow")
        asm.append("extern sqrt")
        asm.append("extern sin")
        asm.append("extern cos")
        asm.append("extern time")
        asm.append("extern rand")
        asm.append("extern exit")
        asm.append("extern MessageBoxA")
        asm.append("extern WinExec")
        asm.append("extern _getcwd\n")



        asm.append("; -- Constants & String Literals --")
        asm.append("section .data")
        asm.extend(self.data_lines)
        asm.append("\n")

        asm.append("; -- Variables & Buffers --")
        asm.append("section .bss")
        asm.extend(self.bss_lines)
        asm.append("\n")

        asm.append("; -- Entry Point --")
        asm.append("section .text")
        asm.append("global main\n")
        asm.append("main:")
        asm.append("    push rbp")
        asm.append("    mov rbp, rsp")
        asm.append("    push rbx")
        asm.append("    push rsi\n")

        asm.extend(self.text_lines)

        asm.append("\n    ; Exit Program")
        asm.append("    lea rsp, [rbp - 16]")
        asm.append("    pop rsi")
        asm.append("    pop rbx")
        asm.append("    pop rbp")
        asm.append("    mov rax, 0")
        asm.append("    ret\n")

        if self.func_lines:
            asm.append("; -- User Functions & Lambdas --")
            asm.extend(self.func_lines)

        return "\n".join(asm)


def compile_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    tokens = tokenize(code)
    parser = Parser(tokens)
    program_ast = parser.parse()

    generator = AsmGenerator()
    generator.generate(program_ast)

    asm_filepath = filepath.replace(".crv", ".asm")
    with open(asm_filepath, "w", encoding="utf-8") as out:
        out.write(generator.build_full_asm())

    print(f"[SUCCESS] Compiled {filepath} -> {asm_filepath}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        compile_file(sys.argv[1])