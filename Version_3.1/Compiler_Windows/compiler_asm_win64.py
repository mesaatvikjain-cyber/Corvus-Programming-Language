# COMPILE TO NASM WIN64 ASSEMBLY (Corvus Compiler Windows Backend v2.0)
import os
import sys

try:
    from Compiler_Core.astnodes import (
        ProgramNode, LiteralNode, IdentifierNode, ListNode, TupleNode, DictNode,
        BinOpNode, UnaryOpNode, SafeNavNode, IndexAccessNode, MethodCallNode,
        VarDeclNode, ConstDeclNode, AssignmentNode, BlockNode, IfNode, WhileNode,
        ForNode, BreakNode, ContinueNode, PassNode, GivoutNode, FuncDeclNode,
        LambdaNode, FuncCallNode, ClassDeclNode, GlobalNode, GetNode, AwaitNode,
        TryErrorNode, InputNode, PipelineNode, MatchNode, CaseNode
    )
    from Compiler_Core.Lexercompiler import tokenize
    from Compiler_Core.parser import Parser
except ImportError:
    try:
        from ..Compiler_Core.astnodes import (
            ProgramNode, LiteralNode, IdentifierNode, ListNode, TupleNode, DictNode,
            BinOpNode, UnaryOpNode, SafeNavNode, IndexAccessNode, MethodCallNode,
            VarDeclNode, ConstDeclNode, AssignmentNode, BlockNode, IfNode, WhileNode,
            ForNode, BreakNode, ContinueNode, PassNode, GivoutNode, FuncDeclNode,
            LambdaNode, FuncCallNode, ClassDeclNode, GlobalNode, GetNode, AwaitNode,
            TryErrorNode, InputNode, PipelineNode, MatchNode, CaseNode
        )
        from ..Compiler_Core.Lexercompiler import tokenize
        from ..Compiler_Core.parser import Parser
    except ImportError:
        from astnodes import (
            ProgramNode, LiteralNode, IdentifierNode, ListNode, TupleNode, DictNode,
            BinOpNode, UnaryOpNode, SafeNavNode, IndexAccessNode, MethodCallNode,
            VarDeclNode, ConstDeclNode, AssignmentNode, BlockNode, IfNode, WhileNode,
            ForNode, BreakNode, ContinueNode, PassNode, GivoutNode, FuncDeclNode,
            LambdaNode, FuncCallNode, ClassDeclNode, GlobalNode, GetNode, AwaitNode,
            TryErrorNode, InputNode, PipelineNode, MatchNode, CaseNode
        )
        from Lexercompiler import tokenize
        from parser import Parser


class AsmGeneratorWin64:
    def __init__(self):
        self.data_lines = []
        self.bss_lines = []
        self.text_lines = []
        self.func_lines = []
        self.string_count = 0
        self.label_count = 0
        self.lambda_count = 0
        self.declared_funcs = set()
        self.loop_stack = []
        self.scope_heap_vars = []  # Scope tracking for deterministic reference counting

    def generate_from_ir(self, ir_program):
        """Code-generate NASM Win64 assembly directly from optimized Three-Address Code (TAC) IR"""
        for instr in ir_program.instructions:
            if instr.op == 'LABEL':
                self.text_lines.append(f"\n{instr.result}:")
            elif instr.op == 'JMP':
                self.text_lines.append(f"    jmp {instr.result}")
            elif instr.op == 'JMP_ZERO':
                self.text_lines.append(f"    cmp rax, 0")
                self.text_lines.append(f"    je {instr.result}")
            elif instr.op == 'ASSIGN':
                if instr.arg1 and instr.arg1.isdigit():
                    self.text_lines.append(f"    mov rax, {instr.arg1}")
                elif instr.arg1:
                    self.text_lines.append(f"    mov rax, [{instr.arg1}]")
                self.text_lines.append(f"    mov [{instr.result}], rax")
            elif instr.op == '+':
                self.text_lines.append(f"    mov rax, [{instr.arg1}]")
                self.text_lines.append(f"    add rax, [{instr.arg2}]")
                self.text_lines.append(f"    mov [{instr.result}], rax")
            elif instr.op == 'RET':
                self.text_lines.append("    mov rsp, rbp")
                self.text_lines.append("    pop rbp")
                self.text_lines.append("    ret")

    def generate(self, node):
        if node is None:
            return

        node_type = type(node).__name__

        if node_type == "ProgramNode":
            for stmt in node.statements:
                self.generate(stmt)

        elif node_type == "LiteralNode":
            if isinstance(node.value, bool):
                val = 1 if node.value else 0
                self.text_lines.append(f"    mov rax, {val}")
            elif isinstance(node.value, (int, float)):
                self.text_lines.append(f"    mov rax, {int(node.value)}")
            elif isinstance(node.value, str):
                lbl = f"msg_{self.string_count}"
                self.string_count += 1
                self.data_lines.append(f'    {lbl} db "{node.value}", 0')
                self.text_lines.append(f"    lea rax, [rel {lbl}]")
            elif node.value is None:
                self.text_lines.append("    mov rax, 0")

        elif node_type == "IdentifierNode":
            self.text_lines.append(f"    mov rax, [{node.name}]")

        elif node_type == "VarDeclNode":
            bss_entry = f"    {node.name} resq 1"
            if bss_entry not in self.bss_lines:
                self.bss_lines.append(bss_entry)
            if node.value is not None:
                self.generate(node.value)
                self.text_lines.append(f"    mov [{node.name}], rax")

        elif node_type == "ConstDeclNode":
            bss_entry = f"    {node.name} resq 1"
            if bss_entry not in self.bss_lines:
                self.bss_lines.append(bss_entry)
            self.generate(node.value)
            self.text_lines.append(f"    mov [{node.name}], rax")

        elif node_type == "AssignmentNode":
            self.generate(node.value)
            if isinstance(node.target, IdentifierNode):
                self.text_lines.append(f"    mov [{node.target.name}], rax")
            elif isinstance(node.target, IndexAccessNode):
                self.generate(node.target.target)
                self.text_lines.append("    push rax")
                self.generate(node.target.index)
                self.text_lines.append("    mov rcx, rax")
                self.text_lines.append("    pop rbx")
                self.generate(node.value)
                self.text_lines.append("    mov [rbx + rcx * 8 + 8], rax")
            else:
                target_name = getattr(node.target, "name", str(node.target))
                self.text_lines.append(f"    mov [{target_name}], rax")

        elif node_type == "BinOpNode":
            self.generate(node.left)
            self.text_lines.append("    push rax")
            self.generate(node.right)
            self.text_lines.append("    mov rbx, rax")
            self.text_lines.append("    pop rax")

            if node.op == '+':
                self.text_lines.append("    add rax, rbx")
            elif node.op == '-':
                self.text_lines.append("    sub rax, rbx")
            elif node.op == '*':
                self.text_lines.append("    imul rax, rbx")
            elif node.op == '/':
                self.text_lines.append("    cqo")
                self.text_lines.append("    idiv rbx")
            elif node.op == '%':
                self.text_lines.append("    cqo")
                self.text_lines.append("    idiv rbx")
                self.text_lines.append("    mov rax, rdx")
            elif node.op == '**':
                self.text_lines.append("    mov rcx, rbx")
                self.text_lines.append("    mov rbx, rax")
                self.text_lines.append("    mov rax, 1")
                lbl = f"pow_loop_{self.label_count}"
                lbl_end = f"pow_end_{self.label_count}"
                self.label_count += 1
                self.text_lines.append(f"{lbl}:")
                self.text_lines.append("    cmp rcx, 0")
                self.text_lines.append(f"    jle {lbl_end}")
                self.text_lines.append("    imul rax, rbx")
                self.text_lines.append("    dec rcx")
                self.text_lines.append(f"    jmp {lbl}")
                self.text_lines.append(f"{lbl_end}:")
            elif node.op in ('==', '!=', '<', '>', '<=', '>='):
                self.text_lines.append("    cmp rax, rbx")
                set_instr = {
                    '==': 'sete', '!=': 'setne',
                    '<': 'setl', '>': 'setg',
                    '<=': 'setle', '>=': 'setge'
                }[node.op]
                self.text_lines.append(f"    {set_instr} al")
                self.text_lines.append("    movzx rax, al")
            elif node.op == 'and':
                self.text_lines.append("    and rax, rbx")
            elif node.op == 'or':
                self.text_lines.append("    or rax, rbx")
            elif node.op == 'xor':
                self.text_lines.append("    xor rax, rbx")
            elif node.op == '??':
                lbl_done = f"null_coal_done_{self.label_count}"
                self.label_count += 1
                self.text_lines.append("    cmp rax, 0")
                self.text_lines.append(f"    jne {lbl_done}")
                self.text_lines.append("    mov rax, rbx")
                self.text_lines.append(f"{lbl_done}:")

        elif node_type == "UnaryOpNode":
            self.generate(node.operand)
            if node.op == '-':
                self.text_lines.append("    neg rax")
            elif node.op == 'not':
                self.text_lines.append("    cmp rax, 0")
                self.text_lines.append("    sete al")
                self.text_lines.append("    movzx rax, al")

        elif node_type == "BlockNode":
            for stmt in node.statements:
                self.generate(stmt)

        elif node_type == "IfNode":
            else_label = f"else_{self.label_count}"
            end_label = f"endif_{self.label_count}"
            self.label_count += 1

            self.generate(node.condition)
            self.text_lines.append("    cmp rax, 0")
            self.text_lines.append(f"    je {else_label}")

            self.generate(node.then_block)
            self.text_lines.append(f"    jmp {end_label}")
            self.text_lines.append(f"{else_label}:")

            if node.elsif_branches:
                for cond, block in node.elsif_branches:
                    next_elsif = f"elsif_{self.label_count}"
                    self.label_count += 1
                    self.generate(cond)
                    self.text_lines.append("    cmp rax, 0")
                    self.text_lines.append(f"    je {next_elsif}")
                    self.generate(block)
                    self.text_lines.append(f"    jmp {end_label}")
                    self.text_lines.append(f"{next_elsif}:")

            if node.else_block:
                self.generate(node.else_block)

            self.text_lines.append(f"{end_label}:")

        elif node_type == "WhileNode":
            start_label = f"while_start_{self.label_count}"
            end_label = f"while_end_{self.label_count}"
            self.label_count += 1
            self.loop_stack.append((start_label, end_label))

            self.text_lines.append(f"{start_label}:")
            self.generate(node.condition)
            self.text_lines.append("    cmp rax, 0")
            self.text_lines.append(f"    je {end_label}")
            self.generate(node.body)
            self.text_lines.append(f"    jmp {start_label}")
            self.text_lines.append(f"{end_label}:")
            self.loop_stack.pop()

        elif node_type == "ForNode":
            start_label = f"for_start_{self.label_count}"
            end_label = f"for_end_{self.label_count}"
            self.label_count += 1
            self.loop_stack.append((start_label, end_label))

            bss_var = f"    {node.iterator} resq 1"
            bss_idx = f"    {node.iterator}_index resq 1"
            if bss_var not in self.bss_lines:
                self.bss_lines.append(bss_var)
            if bss_idx not in self.bss_lines:
                self.bss_lines.append(bss_idx)

            self.generate(node.collection)
            self.text_lines.append("    push rax")
            self.text_lines.append(f"    mov qword [{node.iterator}_index], 0")

            self.text_lines.append(f"{start_label}:")
            self.text_lines.append("    mov rax, [rsp]")
            self.text_lines.append(f"    mov rcx, [{node.iterator}_index]")
            self.text_lines.append("    cmp rcx, [rax]")
            self.text_lines.append(f"    jge {end_label}")

            self.text_lines.append("    mov rbx, [rax + rcx * 8 + 8]")
            self.text_lines.append(f"    mov [{node.iterator}], rbx")

            self.generate(node.body)

            self.text_lines.append(f"    inc qword [{node.iterator}_index]")
            self.text_lines.append(f"    jmp {start_label}")
            self.text_lines.append(f"{end_label}:")
            self.text_lines.append("    add rsp, 8")
            self.loop_stack.pop()

        elif node_type == "BreakNode":
            if self.loop_stack:
                _, end_label = self.loop_stack[-1]
                self.text_lines.append(f"    jmp {end_label}")

        elif node_type == "ContinueNode":
            if self.loop_stack:
                start_label, _ = self.loop_stack[-1]
                self.text_lines.append(f"    jmp {start_label}")

        elif node_type == "PassNode":
            self.text_lines.append("    nop")

        elif node_type == "SafeNavNode":
            lbl_null = f"safe_nav_null_{self.label_count}"
            self.label_count += 1
            self.generate(node.target)
            self.text_lines.append("    cmp rax, 0")
            self.text_lines.append(f"    je {lbl_null}")
            self.text_lines.append(f"    mov rax, [rax + {node.property_name}]")
            self.text_lines.append(f"{lbl_null}:")

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

            if callee_name == "log":
                for arg in node.args:
                    self.generate(arg)
                    self.text_lines.append("    mov rdx, rax")
                    label = f"fmt_log_{self.string_count}"
                    self.string_count += 1
                    if isinstance(arg, LiteralNode) and isinstance(arg.value, str):
                        self.data_lines.append(f'    {label} db "%s", 10, 0')
                    else:
                        self.data_lines.append(f'    {label} db "%lld", 10, 0')
                    self.text_lines.append(f"    lea rcx, [rel {label}]")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call printf")
                    self.text_lines.append("    add rsp, 32")

            elif callee_name in ("str", "int", "flo", "bool"):
                if node.args:
                    self.generate(node.args[0])
                else:
                    self.text_lines.append("    mov rax, 0")
            elif callee_name == "type":
                self.generate(node.args[0])
                lbl = f"type_str_{self.string_count}"
                self.string_count += 1
                self.data_lines.append(f'    {lbl} db "str", 0')
                self.text_lines.append(f"    lea rax, [rel {lbl}]")

            elif callee_name == "abs":
                self.generate(node.args[0])
                lbl_id = self.string_count
                self.string_count += 1
                self.text_lines.append("    test rax, rax")
                self.text_lines.append(f"    jge abs_done_{lbl_id}")
                self.text_lines.append("    neg rax")
                self.text_lines.append(f"abs_done_{lbl_id}:")

            elif callee_name == "sum":
                self.generate(node.args[0])
                lbl_id = self.string_count
                self.string_count += 1
                self.text_lines.append("    mov rcx, [rax]")
                self.text_lines.append("    mov rbx, rax")
                self.text_lines.append("    mov rax, 0")
                self.text_lines.append("    mov rdx, 0")
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
                self.text_lines.append("    mov rax, [rbx + 8]")
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

        elif node_type in ("ListNode", "TupleNode"):
            num_elems = len(node.elements)
            total_bytes = (num_elems + 1) * 8
            self.text_lines.append(f"    mov rcx, {total_bytes}")
            self.text_lines.append("    sub rsp, 32")
            self.text_lines.append("    call malloc")
            self.text_lines.append("    add rsp, 32")
            self.text_lines.append(f"    mov qword [rax], {num_elems}")

            self.text_lines.append("    push rax")
            for idx, elem in enumerate(node.elements):
                self.generate(elem)
                self.text_lines.append("    mov rbx, [rsp]")
                self.text_lines.append(f"    mov [rbx + {(idx + 1) * 8}], rax")
            self.text_lines.append("    pop rax")

        elif node_type == "IndexAccessNode":
            self.generate(node.target)
            self.text_lines.append("    push rax")
            self.generate(node.index)
            self.text_lines.append("    pop rbx")
            self.text_lines.append("    mov rax, [rbx + rax * 8 + 8]")

        elif node_type == "MethodCallNode":
            target_name = getattr(node.target, "name", "")
            if node.method_name in ("length", "len"):
                self.generate(node.target)
                self.text_lines.append("    mov rax, [rax]")
            elif target_name in ("math", "system", "gui", "http", "process"):
                if node.method_name == "sqrt":
                    self.generate(node.args[0])
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call sqrt")
                    self.text_lines.append("    add rsp, 32")
                elif node.method_name == "pow":
                    self.generate(node.args[0])
                    self.text_lines.append("    push rax")
                    self.generate(node.args[1])
                    self.text_lines.append("    mov rdx, rax")
                    self.text_lines.append("    pop rcx")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call pow")
                    self.text_lines.append("    add rsp, 32")
                elif node.method_name in ("run", "shell"):
                    self.generate(node.args[0])
                    self.text_lines.append("    mov rcx, rax")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call system")
                    self.text_lines.append("    add rsp, 32")
            elif target_name == "mem":
                if node.method_name == "alloc" and node.args:
                    self.generate(node.args[0])
                    self.text_lines.append("    mov rcx, rax")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call malloc")
                    self.text_lines.append("    add rsp, 32")
                elif node.method_name == "free" and node.args:
                    self.generate(node.args[0])
                    self.text_lines.append("    mov rcx, rax")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call free")
                    self.text_lines.append("    add rsp, 32")
                elif node.method_name in ("stats", "refcount"):
                    self.text_lines.append("    mov rax, 1")
            elif target_name == "ffi":
                if node.method_name == "load" and node.args:
                    self.generate(node.args[0])
                    self.text_lines.append("    mov rcx, rax")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call LoadLibraryA")
                    self.text_lines.append("    add rsp, 32")
                elif node.method_name == "bind" and len(node.args) >= 2:
                    self.generate(node.args[0])
                    self.text_lines.append("    push rax")
                    self.generate(node.args[1])
                    self.text_lines.append("    mov rdx, rax")
                    self.text_lines.append("    pop rcx")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call GetProcAddress")
                    self.text_lines.append("    add rsp, 32")
                elif node.method_name == "call" and node.args:
                    self.generate(node.args[0])
                    if len(node.args) > 1:
                        self.text_lines.append("    push rax")
                        self.generate(node.args[1])
                        self.text_lines.append("    mov rcx, rax")
                        self.text_lines.append("    pop rax")
                    self.text_lines.append("    call rax")
            elif target_name == "crow":
                if node.method_name == "fly" and node.args:
                    self.generate(node.args[0])
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    mov rcx, 0")
                    self.text_lines.append("    mov rdx, 0")
                    self.text_lines.append("    mov r8, rax")
                    self.text_lines.append("    mov r9, 0")
                    self.text_lines.append("    call CreateThread")
                    self.text_lines.append("    add rsp, 32")
                elif node.method_name == "flock" and node.args:
                    self.generate(node.args[0])
                elif node.method_name == "channel":
                    self.text_lines.append("    mov rcx, 64")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call malloc")
                    self.text_lines.append("    add rsp, 32")


        elif node_type == "InputNode":
            if "    input_buffer resq 1" not in self.bss_lines:
                self.bss_lines.append("    input_buffer resq 1")
            if '    fmt_scan_int db "%lld", 0' not in self.data_lines:
                self.data_lines.append('    fmt_scan_int db "%lld", 0')

            if node.prompt is not None:
                self.generate(node.prompt)
                self.text_lines.append("    mov rdx, rax")
                lbl = f"fmt_prompt_{self.string_count}"
                self.string_count += 1
                self.data_lines.append(f'    {lbl} db "%s", 0')
                self.text_lines.append(f"    lea rcx, [rel {lbl}]")
                self.text_lines.append("    sub rsp, 32")
                self.text_lines.append("    call printf")
                self.text_lines.append("    add rsp, 32")

            self.text_lines.append("    lea rcx, [rel fmt_scan_int]")
            self.text_lines.append("    lea rdx, [rel input_buffer]")
            self.text_lines.append("    sub rsp, 32")
            self.text_lines.append("    call scanf")
            self.text_lines.append("    add rsp, 32")
            self.text_lines.append("    mov rax, [input_buffer]")

        elif node_type == "ClassDeclNode":
            self.declared_funcs.add(node.name)
            old_text_lines = self.text_lines
            self.text_lines = self.func_lines

            self.text_lines.append(f"\n{node.name}:")
            self.text_lines.append("    push rbp")
            self.text_lines.append("    mov rbp, rsp")
            self.text_lines.append("    mov rcx, 64")
            self.text_lines.append("    sub rsp, 32")
            self.text_lines.append("    call malloc")
            self.text_lines.append("    add rsp, 32")
            self.text_lines.append("    mov rsp, rbp")
            self.text_lines.append("    pop rbp")
            self.text_lines.append("    ret")

            self.text_lines = old_text_lines

        elif node_type == "GetNode":
            pass

        elif node_type == "TryErrorNode":
            self.generate(node.try_block)
            if node.final_block:
                self.generate(node.final_block)

        elif node_type == "PipelineNode":
            if isinstance(node.right, FuncCallNode):
                node.right.args.insert(0, node.left)
                self.generate(node.right)
            else:
                self.generate(node.left)
                self.text_lines.append("    push rax")
                self.generate(node.right)
                self.text_lines.append("    call rax")
                self.text_lines.append("    add rsp, 8")

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
        asm.append("; Corvus NASM 64-bit Assembly Output (Windows Win64 ABI)")
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
        asm.append("extern system")
        asm.append("extern LoadLibraryA")
        asm.append("extern GetProcAddress")
        asm.append("extern CreateThread")
        asm.append("extern exit\n")

        asm.append("; -- Constants & String Literals --")
        asm.append("section .data")
        asm.append('    msg_err_null db "[Corvus Runtime Panic]: NullPointerError: Attempted to dereference null pointer.", 10, 0')
        asm.append('    msg_err_bounds db "[Corvus Runtime Panic]: IndexError: Array index out of bounds.", 10, 0')
        asm.append('    msg_err_divzero db "[Corvus Runtime Panic]: MathError: Division by zero.", 10, 0')
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

        asm.append("\n; -- Assembly Runtime Safety & Panic Routines (v3.1) --")
        asm.append("__corvus_panic_null:")
        asm.append('    lea rcx, [rel msg_err_null]')
        asm.append("    sub rsp, 32")
        asm.append("    call printf")
        asm.append("    mov rcx, 1")
        asm.append("    call exit")

        asm.append("__corvus_panic_bounds:")
        asm.append('    lea rcx, [rel msg_err_bounds]')
        asm.append("    sub rsp, 32")
        asm.append("    call printf")
        asm.append("    mov rcx, 1")
        asm.append("    call exit")

        asm.append("__corvus_panic_divzero:")
        asm.append('    lea rcx, [rel msg_err_divzero]')
        asm.append("    sub rsp, 32")
        asm.append("    call printf")
        asm.append("    mov rcx, 1")
        asm.append("    call exit")

        return "\n".join(asm)
