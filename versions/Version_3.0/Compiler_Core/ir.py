# Three-Address Code (TAC) Intermediate Representation (IR) Engine for Corvus v3.0

class TACInstruction:
    def __init__(self, op: str, arg1=None, arg2=None, result=None):
        self.op = op          # 'ASSIGN', 'ADD', 'SUB', 'MUL', 'DIV', 'LABEL', 'JMP', 'JMP_ZERO', 'CALL', 'RET', 'ALLOC', 'FREE'
        self.arg1 = arg1      # Operand 1 or Target
        self.arg2 = arg2      # Operand 2
        self.result = result  # Result variable or Destination

    def __repr__(self):
        if self.op == 'LABEL':
            return f"{self.result}:"
        elif self.op in ('JMP', 'JMP_ZERO'):
            return f"{self.op} {self.arg1} -> {self.result}"
        elif self.op == 'ASSIGN':
            return f"{self.result} = {self.arg1}"
        elif self.op in ('CALL', 'RET', 'ALLOC', 'FREE'):
            return f"{self.op} {self.arg1} {self.arg2 or ''} -> {self.result or ''}".strip()
        else:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"


class IRProgram:
    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self, prefix="L"):
        self.label_count += 1
        return f"{prefix}_{self.label_count}"

    def emit(self, op, arg1=None, arg2=None, result=None):
        instr = TACInstruction(op, arg1, arg2, result)
        self.instructions.append(instr)
        return instr


class IRBuilder:
    def __init__(self):
        self.program = IRProgram()

    def build(self, ast_node):
        self.visit(ast_node)
        return self.program

    def visit(self, node):
        if node is None:
            return None

        node_type = type(node).__name__

        if node_type == "ProgramNode":
            for stmt in node.statements:
                self.visit(stmt)
            return None

        elif node_type == "LiteralNode":
            return repr(node.value) if isinstance(node.value, str) else str(node.value)

        elif node_type == "IdentifierNode":
            return node.name

        elif node_type == "VarDeclNode":
            if node.value is not None:
                val = self.visit(node.value)
                self.program.emit('ASSIGN', val, result=node.name)
            return node.name

        elif node_type == "ConstDeclNode":
            val = self.visit(node.value)
            self.program.emit('ASSIGN', val, result=node.name)
            return node.name

        elif node_type == "AssignmentNode":
            val = self.visit(node.value)
            target_name = getattr(node.target, 'name', str(node.target))
            self.program.emit('ASSIGN', val, result=target_name)
            return target_name

        elif node_type == "BinOpNode":
            left_res = self.visit(node.left)
            right_res = self.visit(node.right)
            temp = self.program.new_temp()
            self.program.emit(node.op, left_res, right_res, result=temp)
            return temp

        elif node_type == "UnaryOpNode":
            operand_res = self.visit(node.operand)
            temp = self.program.new_temp()
            self.program.emit(node.op, operand_res, result=temp)
            return temp

        elif node_type == "IfNode":
            cond_res = self.visit(node.condition)
            else_lbl = self.program.new_label("ELSE")
            end_lbl = self.program.new_label("ENDIF")

            self.program.emit('JMP_ZERO', cond_res, result=else_lbl)
            self.visit(node.then_block)
            self.program.emit('JMP', result=end_lbl)
            self.program.emit('LABEL', result=else_lbl)

            if node.else_block:
                self.visit(node.else_block)

            self.program.emit('LABEL', result=end_lbl)
            return None

        elif node_type == "WhileNode":
            start_lbl = self.program.new_label("WHILE_START")
            end_lbl = self.program.new_label("WHILE_END")

            self.program.emit('LABEL', result=start_lbl)
            cond_res = self.visit(node.condition)
            self.program.emit('JMP_ZERO', cond_res, result=end_lbl)
            self.visit(node.body)
            self.program.emit('JMP', result=start_lbl)
            self.program.emit('LABEL', result=end_lbl)
            return None

        elif node_type == "BlockNode":
            for stmt in node.statements:
                self.visit(stmt)
            return None

        elif node_type == "GivoutNode":
            val = self.visit(node.value) if node.value else "0"
            self.program.emit('RET', val)
            return val

        elif node_type == "FuncCallNode":
            args_res = [self.visit(arg) for arg in node.args]
            callee_name = getattr(node.callee, 'name', str(node.callee))
            temp = self.program.new_temp()
            self.program.emit('CALL', callee_name, args_res, result=temp)
            return temp

        return None
