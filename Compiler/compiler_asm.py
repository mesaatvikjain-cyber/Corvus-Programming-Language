# ========================================
# COMPILE TO ASSEMBLY (Corvus Compiler)
# ========================================
from Lexercompiler import tokenize
from parser import Parser
from Interpreter.astnodes import (
    ProgramNode, LiteralNode, IdentifierNode, BinOpNode,
    VarDeclNode, FuncCallNode
)


class AsmGenerator:
    def __init__(self):
        self.data_lines = []     # For string literals & constants
        self.bss_lines = []      # For variables (e.g. x resq 1)
        self.text_lines = []     # For CPU instructions
        self.string_count = 0    # Unique string label counter (msg_0, msg_1...)

    def generate(self, node):
        if node is None:
            return

        node_type = type(node).__name__

        # 1. Program Root Node (List of Statements)
        if node_type == "ProgramNode":
            for stmt in node.statements:
                self.generate(stmt)

        # 2. Literal Values (Numbers, Strings, Booleans)
        elif node_type == "LiteralNode":
            if isinstance(node.value, (int, float)):
                self.text_lines.append(f"    mov rax, {node.value}")
            elif isinstance(node.value, str):
                label = f"msg_{self.string_count}"
                self.string_count += 1
                self.data_lines.append(f'    {label} db "{node.value}", 10, 0')
                self.text_lines.append(f"    mov rax, {label}")

        # 3. Identifier Reference (Variables)
        elif node_type == "IdentifierNode":
            self.text_lines.append(f"    mov rax, [{node.name}]")

        # 4. Function Calls (e.g., log(...))
        elif node_type == "FuncCallNode":
            callee_name = getattr(node.callee, 'name', None)
            if callee_name == "log":
                for arg in node.args:
                    if isinstance(arg, LiteralNode) and isinstance(arg.value, str):
                        label = f"msg_{self.string_count}"
                        self.string_count += 1
                        self.data_lines.append(f'    {label} db "{arg.value}", 10, 0')
                        self.text_lines.append(f"    mov rcx, {label}")
                        self.text_lines.append("    call printf")
                    else:
                        self.generate(arg)
                        self.text_lines.append("    mov rsi, rax")
                        label = f"fmt_int_{self.string_count}"
                        self.string_count += 1
                        self.data_lines.append(f'    {label} db "%d", 10, 0')
                        self.text_lines.append(f"    mov rcx, {label}")
                        self.text_lines.append("    call printf")

        # 5. Variable Declarations (set int x = 5)
        elif node_type == "VarDeclNode":
            self.bss_lines.append(f"    {node.name} resq 1")
            if node.value is not None:
                self.generate(node.value)
                self.text_lines.append(f"    mov [{node.name}], rax")

        # 6. Binary Operators (Math: +, -, *, /)
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

    def build_full_asm(self):
        asm = []
        asm.append("; ========================================")
        asm.append("; Corvus NASM 64-bit Output")
        asm.append("; ========================================")
        asm.append("bits 64")
        asm.append("default rel\n")

        asm.append("; -- External Functions --")
        asm.append("extern ExitProcess")
        asm.append("extern printf\n")

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
        asm.append("    mov rbp, rsp\n")

        asm.extend(self.text_lines)

        asm.append("\n    ; Exit Program")
        asm.append("    mov rsp, rbp")
        asm.append("    pop rbp")
        asm.append("    mov rcx, 0")
        asm.append("    call ExitProcess")

        return "\n".join(asm)


def compile_file(filepath):
    with open(filepath, "r") as f:
        code = f.read()

    tokens = tokenize(code)
    parser = Parser(tokens)
    program_ast = parser.parse()

    generator = AsmGenerator()
    generator.generate(program_ast)

    asm_filepath = filepath.replace(".crv", ".asm")
    with open(asm_filepath, "w") as out:
        out.write(generator.build_full_asm())

    print(f"✅ Successfully compiled {filepath} -> {asm_filepath}")


if __name__ == "__main__":
    compile_file("compiler_test.crv")