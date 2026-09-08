# COMPILE TO NASM MACHO64 ASSEMBLY (Corvus Compiler macOS Backend v2.0)
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


class AsmGeneratorMacOS:
    def __init__(self):
        self.data_lines = []
        self.bss_lines = []
        self.text_lines = []
        self.func_lines = []
        self.string_count = 0
        self.label_count = 0
        self.lambda_count = 0
        self.declared_funcs = set()

    def generate(self, node):
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
            self.text_lines.append(f"    mov rax, [rel _{node.name}]")

        elif node_type == "VarDeclNode":
            bss_entry = f"    _{node.name} resq 1"
            if bss_entry not in self.bss_lines:
                self.bss_lines.append(bss_entry)
            if node.value is not None:
                self.generate(node.value)
                self.text_lines.append(f"    mov [rel _{node.name}], rax")

        elif node_type == "ConstDeclNode":
            bss_entry = f"    _{node.name} resq 1"
            if bss_entry not in self.bss_lines:
                self.bss_lines.append(bss_entry)
            self.generate(node.value)
            self.text_lines.append(f"    mov [rel _{node.name}], rax")

        elif node_type == "AssignmentNode":
            self.generate(node.value)
            if isinstance(node.target, IdentifierNode):
                self.text_lines.append(f"    mov [rel _{node.target.name}], rax")
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
                self.text_lines.append(f"    mov [rel _{target_name}], rax")

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

            self.text_lines.append(f"{start_label}:")
            self.generate(node.condition)
            self.text_lines.append("    cmp rax, 0")
            self.text_lines.append(f"    je {end_label}")
            self.generate(node.body)
            self.text_lines.append(f"    jmp {start_label}")
            self.text_lines.append(f"{end_label}:")

        elif node_type == "ForNode":
            start_label = f"for_start_{self.label_count}"
            end_label = f"for_end_{self.label_count}"
            self.label_count += 1

            bss_var = f"    _{node.iterator} resq 1"
            bss_idx = f"    _{node.iterator}_index resq 1"
            if bss_var not in self.bss_lines:
                self.bss_lines.append(bss_var)
            if bss_idx not in self.bss_lines:
                self.bss_lines.append(bss_idx)

            self.generate(node.collection)
            self.text_lines.append("    push rax")
            self.text_lines.append(f"    mov qword [rel _{node.iterator}_index], 0")

            self.text_lines.append(f"{start_label}:")
            self.text_lines.append("    mov rax, [rsp]")
            self.text_lines.append(f"    mov rcx, [rel _{node.iterator}_index]")
            self.text_lines.append("    cmp rcx, [rax]")
            self.text_lines.append(f"    jge {end_label}")

            self.text_lines.append("    mov rbx, [rax + rcx * 8 + 8]")
            self.text_lines.append(f"    mov [rel _{node.iterator}], rbx")

            self.generate(node.body)

            self.text_lines.append(f"    inc qword [rel _{node.iterator}_index]")
            self.text_lines.append(f"    jmp {start_label}")
            self.text_lines.append(f"{end_label}:")
            self.text_lines.append("    add rsp, 8")

        elif node_type == "FuncDeclNode":
            self.declared_funcs.add(node.name)
            for param in node.params:
                bss_entry = f"    _{param} resq 1"
                if bss_entry not in self.bss_lines:
                    self.bss_lines.append(bss_entry)

            old_text_lines = self.text_lines
            self.text_lines = self.func_lines

            self.text_lines.append(f"\n_{node.name}:")
            self.text_lines.append("    push rbp")
            self.text_lines.append("    mov rbp, rsp")

            sysv_regs = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
            for i, param in enumerate(node.params):
                if i < len(sysv_regs):
                    self.text_lines.append(f"    mov [rel _{param}], {sysv_regs[i]}")
                else:
                    offset = 16 + ((i - len(sysv_regs)) * 8)
                    self.text_lines.append(f"    mov rax, [rbp + {offset}]")
                    self.text_lines.append(f"    mov [rel _{param}], rax")

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
                    self.text_lines.append("    mov rsi, rax")
                    label = f"fmt_log_{self.string_count}"
                    self.string_count += 1
                    if isinstance(arg, LiteralNode) and isinstance(arg.value, str):
                        self.data_lines.append(f'    {label} db "%s", 10, 0')
                    else:
                        self.data_lines.append(f'    {label} db "%lld", 10, 0')
                    self.text_lines.append(f"    lea rdi, [rel {label}]")
                    self.text_lines.append("    mov rax, 0")
                    self.text_lines.append("    call _printf")
            else:
                sysv_regs = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
                num_args = len(node.args)
                for idx, arg in enumerate(node.args):
                    self.generate(arg)
                    if idx < len(sysv_regs):
                        self.text_lines.append(f"    mov {sysv_regs[idx]}, rax")
                    else:
                        self.text_lines.append("    push rax")

                if callee_name and callee_name in self.declared_funcs:
                    self.text_lines.append(f"    call _{callee_name}")
                elif callee_name:
                    self.text_lines.append(f"    mov rax, [rel _{callee_name}]")
                    self.text_lines.append("    call rax")
                else:
                    self.generate(node.callee)
                    self.text_lines.append("    call rax")

                if num_args > len(sysv_regs):
                    self.text_lines.append(f"    add rsp, {(num_args - len(sysv_regs)) * 8}")

        elif node_type == "LambdaNode":
            lbl_name = f"lambda_{self.lambda_count}"
            self.lambda_count += 1

            for param in node.params:
                bss_entry = f"    _{param} resq 1"
                if bss_entry not in self.bss_lines:
                    self.bss_lines.append(bss_entry)

            old_text = self.text_lines
            self.text_lines = self.func_lines

            self.text_lines.append(f"\n_{lbl_name}:")
            self.text_lines.append("    push rbp")
            self.text_lines.append("    mov rbp, rsp")

            sysv_regs = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
            for i, param in enumerate(node.params):
                if i < len(sysv_regs):
                    self.text_lines.append(f"    mov [rel _{param}], {sysv_regs[i]}")
                else:
                    offset = 16 + ((i - len(sysv_regs)) * 8)
                    self.text_lines.append(f"    mov rax, [rbp + {offset}]")
                    self.text_lines.append(f"    mov [rel _{param}], rax")

            self.generate(node.body)
            self.text_lines.append("    mov rsp, rbp")
            self.text_lines.append("    pop rbp")
            self.text_lines.append("    ret")

            self.text_lines = old_text
            self.text_lines.append(f"    lea rax, [rel _{lbl_name}]")

        elif node_type in ("ListNode", "TupleNode"):
            num_elems = len(node.elements)
            total_bytes = (num_elems + 1) * 8
            self.text_lines.append(f"    mov rdi, {total_bytes}")
            self.text_lines.append("    call _malloc")
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

        elif node_type == "PipelineNode":
            if isinstance(node.right, FuncCallNode):
                node.right.args.insert(0, node.left)
                self.generate(node.right)
            else:
                self.generate(node.left)
                self.text_lines.append("    mov rdi, rax")
                self.generate(node.right)
                self.text_lines.append("    call rax")

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
        asm.append("; Corvus NASM 64-bit Assembly Output (macOS Mach-O System V ABI)")
        asm.append("; Author: Saatvik Jain")
        asm.append("; ========================================")
        asm.append("bits 64")
        asm.append("default rel\n")

        asm.append("; -- External C Runtime Functions (Mach-O Leading Underscore) --")
        asm.append("extern _printf")
        asm.append("extern _scanf")
        asm.append("extern _malloc")
        asm.append("extern _free")
        asm.append("extern _pow")
        asm.append("extern _sqrt")
        asm.append("extern _exit\n")

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
        asm.append("global _main\n")
        asm.append("_main:")
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
