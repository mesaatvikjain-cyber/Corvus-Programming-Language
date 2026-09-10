# Corvus v4.1 Super High-Level IR Optimization Engine
# Advanced Passes: Constant Propagation, Algebraic Strength Reduction, Branch Folding, CFG Jump Threading

from ir import TACInstruction, IRProgram

class SuperOptimizer:
    def __init__(self, ir_program: IRProgram):
        self.program = ir_program

    def optimize(self):
        """Runs aggressive multi-pass super optimization pipeline"""
        self.constant_propagation_pass()
        self.strength_reduction_pass()
        self.branch_folding_pass()
        self.jump_threading_pass()
        return self.program

    def constant_propagation_pass(self):
        """Pass 1: Constant Propagation across basic blocks"""
        known_constants = {}  # var_name -> str(constant_value)
        new_instructions = []

        for instr in self.program.instructions:
            if instr.op in ('LABEL', 'CALL', 'JMP', 'JMP_ZERO'):
                known_constants.clear()
                new_instructions.append(instr)
                continue

            # Substitute known constant arguments into current instruction
            arg1 = str(instr.arg1) if instr.arg1 is not None else None
            arg2 = str(instr.arg2) if instr.arg2 is not None else None

            if arg1 and arg1 in known_constants:
                arg1 = known_constants[arg1]
            if arg2 and arg2 in known_constants:
                arg2 = known_constants[arg2]

            instr.arg1 = arg1
            instr.arg2 = arg2

            if instr.op == 'ASSIGN':
                if self._to_number(instr.arg1) is not None:
                    known_constants[instr.result] = str(instr.arg1)
                elif instr.result in known_constants:
                    del known_constants[instr.result]

            new_instructions.append(instr)

        self.program.instructions = new_instructions

    def strength_reduction_pass(self):
        """Pass 2: Algebraic Simplifications & Power-of-2 Bitwise Strength Reduction"""
        new_instructions = []

        for instr in self.program.instructions:
            if instr.op in ('*', '/', '+', '-', '**'):
                val1 = self._to_number(instr.arg1)
                val2 = self._to_number(instr.arg2)

                # Rule 1: Algebraic Simplifications
                if instr.op == '*':
                    if val1 == 0 or val2 == 0:
                        new_instructions.append(TACInstruction('ASSIGN', '0', result=instr.result))
                        continue
                    elif val1 == 1:
                        new_instructions.append(TACInstruction('ASSIGN', str(instr.arg2), result=instr.result))
                        continue
                    elif val2 == 1:
                        new_instructions.append(TACInstruction('ASSIGN', str(instr.arg1), result=instr.result))
                        continue
                elif instr.op == '+':
                    if val1 == 0:
                        new_instructions.append(TACInstruction('ASSIGN', str(instr.arg2), result=instr.result))
                        continue
                    elif val2 == 0:
                        new_instructions.append(TACInstruction('ASSIGN', str(instr.arg1), result=instr.result))
                        continue
                elif instr.op == '-':
                    if val2 == 0:
                        new_instructions.append(TACInstruction('ASSIGN', str(instr.arg1), result=instr.result))
                        continue

                # Rule 2: Bitwise Strength Reduction for Powers of 2
                if instr.op == '*' and isinstance(val2, int) and val2 > 0 and (val2 & (val2 - 1)) == 0:
                    shift_amount = val2.bit_length() - 1
                    new_instructions.append(TACInstruction('SHL', str(instr.arg1), str(shift_amount), result=instr.result))
                    continue
                elif instr.op == '/' and isinstance(val2, int) and val2 > 0 and (val2 & (val2 - 1)) == 0:
                    shift_amount = val2.bit_length() - 1
                    new_instructions.append(TACInstruction('SHR', str(instr.arg1), str(shift_amount), result=instr.result))
                    continue

            new_instructions.append(instr)

        self.program.instructions = new_instructions

    def branch_folding_pass(self):
        """Pass 3: Constant Branch Folding and Dead Conditional Elimination"""
        new_instructions = []

        for instr in self.program.instructions:
            if instr.op == 'JMP_ZERO':
                val = self._to_number(instr.arg1)
                if val is not None:
                    if val == 0 or val is False:
                        # Condition is always zero/false -> Unconditional Jump
                        new_instructions.append(TACInstruction('JMP', result=instr.result))
                        continue
                    else:
                        # Condition is non-zero/true -> Jump never taken (no-op)
                        continue

            new_instructions.append(instr)

        self.program.instructions = new_instructions

    def jump_threading_pass(self):
        """Pass 4: Control Flow Graph (CFG) Jump Threading"""
        label_redirects = {}
        n = len(self.program.instructions)

        for i in range(n - 1):
            curr = self.program.instructions[i]
            nxt = self.program.instructions[i + 1]
            if curr.op == 'LABEL' and nxt.op == 'JMP':
                label_redirects[curr.result] = nxt.result

        if not label_redirects:
            return

        for instr in self.program.instructions:
            if instr.op in ('JMP', 'JMP_ZERO') and instr.result in label_redirects:
                # Follow jump chain to final target
                target = instr.result
                visited = set()
                while target in label_redirects and target not in visited:
                    visited.add(target)
                    target = label_redirects[target]
                instr.result = target

    def _to_number(self, val_str):
        if val_str is None:
            return None
        try:
            s = str(val_str)
            if s.lower() == 'true': return 1
            if s.lower() == 'false': return 0
            if '.' in s:
                return float(s)
            return int(s)
        except ValueError:
            return None
