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
        self.text_lines = []     # For CPU instructions in main
        self.func_lines = []     # For user function definitions
        self.string_count = 0    # Unique string label counter (msg_0, msg_1...)


    def generate(self, node):
        if node is None:
            return

        node_type = type(node).__name__

        # 1. Program Root Node & Code Blocks
        if node_type in ("ProgramNode", "BlockNode"):
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

        # 4. Function Calls (e.g., log(...) or custom functions)
        elif node_type == "FuncCallNode":
            callee_name = getattr(node.callee, 'name', None)
            if callee_name == "log":
                for arg in node.args:
                    if isinstance(arg, LiteralNode) and isinstance(arg.value, str):
                        label = f"msg_{self.string_count}"
                        self.string_count += 1
                        self.data_lines.append(f'    {label} db "{arg.value}", 10, 0')
                        self.text_lines.append(f"    mov rcx, {label}")
                        self.text_lines.append("    sub rsp, 32")
                        self.text_lines.append("    call printf")
                        self.text_lines.append("    add rsp, 32")
                    else:
                        self.generate(arg)
                        self.text_lines.append("    mov rdx, rax")
                        label = f"fmt_int_{self.string_count}"
                        self.string_count += 1
                        self.data_lines.append(f'    {label} db "%d", 10, 0')
                        self.text_lines.append(f"    mov rcx, {label}")
                        self.text_lines.append("    sub rsp, 32")
                        self.text_lines.append("    call printf")
                        self.text_lines.append("    add rsp, 32")

            else:
                for arg in reversed(node.args):
                    self.generate(arg)
                    self.text_lines.append("    push rax")
                if callee_name:
                    self.text_lines.append(f"    call {callee_name}")
                else:
                    raise NotImplementedError("Dynamic function calls are not supported.")
                if node.args:
                    self.text_lines.append(f"    add rsp, {len(node.args) * 8}")


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
            elif node.op == "/":
                self.text_lines.append("    cqo")  # Sign extend rax into rdx:rax
                self.text_lines.append("    idiv rbx")
            elif node.op == "%":
                self.text_lines.append("    cqo")  # Sign extend rax into rdx:rax
                self.text_lines.append("    idiv rbx")
                self.text_lines.append("    mov rax, rdx")  # Remainder is in rdx
            elif node.op == "**":
                self.text_lines.append("    mov rcx, rbx")  # Exponent in rcx
                self.text_lines.append("    mov rbx, rax")  # Base in rbx
                self.text_lines.append("    mov rax, 1")    # Result starts at 1
                self.text_lines.append("power_loop:")
                self.text_lines.append("    test rcx, rcx")
                self.text_lines.append("    jz power_done")
                self.text_lines.append("    imul rax, rbx")
                self.text_lines.append("    dec rcx")
                self.text_lines.append("    jmp power_loop")
                self.text_lines.append("power_done:")
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
        elif node_type=="IfNode":
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

        elif node_type=="WhileNode":
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
        elif node_type=="FuncDeclNode":
            # 1. Register parameter variables in .bss
            for param in node.params:
                bss_entry = f"    {param} resq 1"
                if bss_entry not in self.bss_lines:
                    self.bss_lines.append(bss_entry)

            # 2. Target func_lines
            old_text_lines = self.text_lines
            self.text_lines = self.func_lines
            
            self.text_lines.append(f"\n{node.name}:")
            self.text_lines.append("    push rbp")
            self.text_lines.append("    mov rbp, rsp")

            # 3. Read passed stack arguments ([rbp + 16], [rbp + 24], ...) into parameter variables
            for i, param in enumerate(node.params):
                offset = 16 + (i * 8)
                self.text_lines.append(f"    mov rax, [rbp + {offset}]")
                self.text_lines.append(f"    mov [{param}], rax")

            self.generate(node.body)
            self.text_lines.append("    mov rsp, rbp")
            self.text_lines.append("    pop rbp")
            self.text_lines.append("    ret")
            
            self.text_lines = old_text_lines

        elif node_type=="GivoutNode":
            self.generate(node.value)
            self.text_lines.append("    ret")

        elif node_type=="AssignmentNode":
            self.generate(node.value)
            self.text_lines.append(f"    mov [{node.target.name}], rax")

        elif node_type=="UnaryOpNode":
            self.generate(node.operand)
            if node.op == "-":
                self.text_lines.append("    neg rax")
            elif node.op == "not":
                self.text_lines.append("    cmp rax, 0")
                self.text_lines.append("    sete al")
                self.text_lines.append("    movzx rax, al")
        elif node_type=="BreakNode":
            self.text_lines.append("    jmp break_label")
        elif node_type=="ContinueNode":
            self.text_lines.append("    jmp continue_label")
        elif node_type=="PassNode":
            self.text_lines.append("    nop")
        elif node_type=="ForNode":
            for var in (node.iterator, f"{node.iterator}_collection", f"{node.iterator}_index"):
                bss_entry = f"    {var} resq 1"
                if bss_entry not in self.bss_lines:
                    self.bss_lines.append(bss_entry)

            label_id = self.string_count
            self.string_count += 1
            start_label = f"for_start_{label_id}"
            end_label = f"for_end_{label_id}"
            continue_label = f"for_continue_{label_id}"

            # 1. Generate code for the collection and store it in a temporary variable
            self.generate(node.collection)
            self.text_lines.append(f"    mov [{node.iterator}_collection], rax")

            # 2. Initialize the iterator variable to 0
            self.text_lines.append(f"    mov [{node.iterator}_index], 0")

            # 3. Start of the loop
            self.text_lines.append(f"{start_label}:")
            self.text_lines.append(f"    mov rax, [{node.iterator}_collection]")
            self.text_lines.append(f"    mov rcx, [{node.iterator}_index]")
            self.text_lines.append(f"    cmp rcx, [rax]")  # Assuming the first element is the length
            self.text_lines.append(f"    jge {end_label}")

            # 4. Load the current item into the iterator variable
            self.text_lines.append(f"    mov rbx, [rax + rcx * 8 + 8]")  # Assuming items start after length
            self.text_lines.append(f"    mov [{node.iterator}], rbx")

            # 5. Generate code for the loop body
            self.generate(node.body)

            # 6. Increment the iterator index and jump back to the start of the loop
            self.text_lines.append(f"{continue_label}:")
            self.text_lines.append(f"    inc [{node.iterator}_index]")
            self.text_lines.append(f"    jmp {start_label}")

            # 7. End of the loop
            self.text_lines.append(f"{end_label}:")
        elif node_type=="SafeNavNode":
            self.generate(node.target)
            self.text_lines.append("    cmp rax, 0")
            safe_nav_label = f"safe_nav_{self.string_count}"
            self.string_count += 1
            self.text_lines.append(f"    je {safe_nav_label}")
            self.text_lines.append(f"    mov rax, [rax + {node.property_name}]")
            self.text_lines.append(f"{safe_nav_label}:")
        elif node_type=="IndexAccessNode":
            self.generate(node.target)
            self.text_lines.append("    push rax")
            self.generate(node.index)
            self.text_lines.append("    pop rbx")
            self.text_lines.append("    mov rax, [rbx + rax * 8]")  # Assuming 8-byte elements
        elif node_type=="MethodCallNode":
            self.generate(node.target)
            self.text_lines.append("    push rax")
            for arg in reversed(node.args):
                self.generate(arg)
                self.text_lines.append("    push rax")
            self.text_lines.append("    pop rbx")  # Restore target object
            self.text_lines.append(f"    call {node.method_name}")
            if node.args:
                self.text_lines.append(f"    add rsp, {len(node.args) * 8}")  # Clean up arguments
        elif node_type=="ConstDeclNode":
            bss_entry = f"    {node.name} resq 1"
            if bss_entry not in self.bss_lines:
                self.bss_lines.append(bss_entry)
            self.generate(node.value)
            self.text_lines.append(f"    mov [{node.name}], rax")

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
                    self.text_lines.append(f"    mov rcx, {label}")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call printf")
                    self.text_lines.append("    add rsp, 32")
                else:
                    self.generate(node.prompt)
                    self.text_lines.append("    mov rdx, rax")
                    label = f"fmt_int_{self.string_count}"
                    self.string_count += 1
                    self.data_lines.append(f'    {label} db "%d", 0')
                    self.text_lines.append(f"    mov rcx, {label}")
                    self.text_lines.append("    sub rsp, 32")
                    self.text_lines.append("    call printf")
                    self.text_lines.append("    add rsp, 32")

            self.text_lines.append("    mov rcx, fmt_scan_int")
            self.text_lines.append("    mov rdx, input_buffer")
            self.text_lines.append("    sub rsp, 32")
            self.text_lines.append("    call scanf")
            self.text_lines.append("    add rsp, 32")
            self.text_lines.append("    mov rax, [input_buffer]")

        
        
    def build_full_asm(self):
        asm = []
        asm.append("; ========================================")
        asm.append("; Corvus NASM 64-bit Output")
        asm.append("; ========================================")
        asm.append("bits 64")
        asm.append("default rel\n")

        asm.append("; -- External Functions --")
        asm.append("extern ExitProcess")
        asm.append("extern printf")
        asm.append("extern scanf\n")


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
        asm.append("    call ExitProcess\n")

        if self.func_lines:
            asm.append("; -- User Defined Functions --")
            asm.extend(self.func_lines)

        return "\n".join(asm)


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

    print(f"[SUCCESS] Compiled {filepath} -> {asm_filepath}")


if __name__ == "__main__":
    compile_file("compiler_test.crv")