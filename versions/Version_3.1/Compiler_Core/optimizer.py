# Corvus v3.0 IR Optimizer: Constant Folding & Dead Code Elimination (DCE) Pass

from ir import TACInstruction, IRProgram

class IROptimizer:
    def __init__(self, ir_program: IRProgram):
        self.program = ir_program

    def optimize(self):
        self.constant_folding_pass()
        self.dead_code_elimination_pass()
        return self.program

    def constant_folding_pass(self):
        """Pass 1: Evaluate constant expressions at compile-time (e.g. 2 + 3 -> 5)"""
        new_instructions = []
        for instr in self.program.instructions:
            if instr.op in ('+', '-', '*', '/', '%', '**'):
                # Try parsing arg1 and arg2 as numeric literals
                val1 = self._to_number(instr.arg1)
                val2 = self._to_number(instr.arg2)

                if val1 is not None and val2 is not None:
                    res_val = None
                    if instr.op == '+':    res_val = val1 + val2
                    elif instr.op == '-':  res_val = val1 - val2
                    elif instr.op == '*':  res_val = val1 * val2
                    elif instr.op == '/' and val2 != 0: res_val = val1 // val2 if isinstance(val1, int) and isinstance(val2, int) else val1 / val2
                    elif instr.op == '%':  res_val = val1 % val2
                    elif instr.op == '**': res_val = val1 ** val2

                    if res_val is not None:
                        # Replace binop instruction with constant assignment TAC
                        new_instructions.append(TACInstruction('ASSIGN', str(res_val), result=instr.result))
                        continue

            new_instructions.append(instr)

        self.program.instructions = new_instructions

    def dead_code_elimination_pass(self):
        """Pass 2: Remove unreachable code after returns/jumps and unused temporary variables"""
        used_variables = set()
        for instr in self.program.instructions:
            if instr.arg1 and not instr.arg1.startswith('"'):
                used_variables.add(instr.arg1)
            if instr.arg2 and not instr.arg2.startswith('"'):
                used_variables.add(instr.arg2)

        new_instructions = []
        unreachable = False

        for instr in self.program.instructions:
            if instr.op == 'LABEL':
                unreachable = False

            if unreachable:
                continue

            # Eliminate unused temporary assignments (t1 = ...) if t1 is never read
            if instr.op == 'ASSIGN' and instr.result.startswith('t') and instr.result not in used_variables:
                continue

            new_instructions.append(instr)

            if instr.op in ('JMP', 'RET'):
                unreachable = True

        self.program.instructions = new_instructions

    def _to_number(self, val_str):
        if val_str is None:
            return None
        try:
            if '.' in str(val_str):
                return float(val_str)
            return int(val_str)
        except ValueError:
            return None
