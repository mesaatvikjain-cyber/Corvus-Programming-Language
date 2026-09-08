# Corvus v4.0 Advanced TAC IR Optimizer Engine
# Passes: Constant Folding, Common Subexpression Elimination (CSE), Loop Unrolling, Function Inlining, Dead Code Elimination (DCE)

from ir import TACInstruction, IRProgram

class IROptimizer:
    def __init__(self, ir_program: IRProgram):
        self.program = ir_program

    def optimize(self):
        """Executes full optimization pipeline on TAC IR representation"""
        self.constant_folding_pass()
        self.common_subexpression_elimination_pass()
        self.loop_unrolling_pass()
        self.inlining_pass()
        self.dead_code_elimination_pass()
        return self.program

    def constant_folding_pass(self):
        """Pass 1: Compile-time evaluation of constant expressions (e.g., 5 * 10 -> 50)"""
        new_instructions = []
        for instr in self.program.instructions:
            if instr.op in ('+', '-', '*', '/', '%', '**'):
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
                        new_instructions.append(TACInstruction('ASSIGN', str(res_val), result=instr.result))
                        continue

            new_instructions.append(instr)

        self.program.instructions = new_instructions

    def common_subexpression_elimination_pass(self):
        """Pass 2: Common Subexpression Elimination (CSE) across basic blocks"""
        new_instructions = []
        seen_expressions = {}  # Key: (op, arg1, arg2) -> Result variable

        for instr in self.program.instructions:
            if instr.op in ('LABEL', 'JMP', 'JMP_ZERO', 'CALL', 'RET'):
                # Reset available expressions across control flow boundaries
                seen_expressions.clear()
                new_instructions.append(instr)
                continue

            if instr.op in ('+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>='):
                expr_key = (instr.op, str(instr.arg1), str(instr.arg2))
                if expr_key in seen_expressions:
                    # Reuse existing computed target variable
                    existing_var = seen_expressions[expr_key]
                    new_instructions.append(TACInstruction('ASSIGN', existing_var, result=instr.result))
                    continue
                else:
                    seen_expressions[expr_key] = instr.result

            # If a variable in seen expressions is modified, invalidate dependent expressions
            if instr.op == 'ASSIGN':
                keys_to_remove = [k for k, v in seen_expressions.items() if k[1] == instr.result or k[2] == instr.result]
                for k in keys_to_remove:
                    del seen_expressions[k]

            new_instructions.append(instr)

        self.program.instructions = new_instructions

    def loop_unrolling_pass(self, max_unroll_iterations=4):
        """Pass 3: Unrolls small fixed-bound loop blocks in TAC instructions"""
        new_instructions = []
        i = 0
        n = len(self.program.instructions)

        while i < n:
            instr = self.program.instructions[i]
            # Pattern check for simple while/for loops with constant trip count
            if (instr.op == 'LABEL' and instr.result and instr.result.startswith('WHILE_START') and
                i + 4 < n and self.program.instructions[i+1].op in ('<', '<=', '>', '>=') and
                self.program.instructions[i+2].op == 'JMP_ZERO'):
                
                cond_instr = self.program.instructions[i+1]
                val1 = self._to_number(cond_instr.arg1)
                val2 = self._to_number(cond_instr.arg2)

                if val1 is not None and val2 is not None:
                    # Deterministic small loop bound detected
                    trip_count = abs(int(val2 - val1))
                    if 0 < trip_count <= max_unroll_iterations:
                        # Find loop body end
                        end_label = self.program.instructions[i+2].result
                        body = []
                        j = i + 3
                        while j < n and not (self.program.instructions[j].op == 'LABEL' and self.program.instructions[j].result == end_label):
                            if self.program.instructions[j].op != 'JMP':
                                body.append(self.program.instructions[j])
                            j += 1
                        
                        # Emit unrolled iterations
                        for iter_idx in range(trip_count):
                            for b_instr in body:
                                new_instructions.append(TACInstruction(b_instr.op, b_instr.arg1, b_instr.arg2, b_instr.result))
                        
                        i = j + 1
                        continue

            new_instructions.append(instr)
            i += 1

        self.program.instructions = new_instructions

    def inlining_pass(self):
        """Pass 4: Function Inlining for small leaf functions"""
        # Collect simple inline function definitions
        func_definitions = {}  # func_name -> list of TAC instructions
        current_func = None
        current_body = []

        for instr in self.program.instructions:
            if instr.op == 'LABEL' and instr.result and instr.result.startswith('FUNC_'):
                current_func = instr.result
                current_body = []
            elif current_func:
                if instr.op == 'RET':
                    # Only inline leaf functions with <= 6 TAC instructions
                    if len(current_body) <= 6 and not any(b.op == 'CALL' for b in current_body):
                        func_definitions[current_func] = current_body
                    current_func = None
                else:
                    current_body.append(instr)

        if not func_definitions:
            return

        new_instructions = []
        for instr in self.program.instructions:
            if instr.op == 'CALL' and f"FUNC_{instr.arg1}" in func_definitions:
                inlined_body = func_definitions[f"FUNC_{instr.arg1}"]
                # Substitute argument values into inlined body
                for b_instr in inlined_body:
                    new_instructions.append(TACInstruction(b_instr.op, b_instr.arg1, b_instr.arg2, b_instr.result))
                continue
            new_instructions.append(instr)

        self.program.instructions = new_instructions

    def dead_code_elimination_pass(self):
        """Pass 5: Remove unreachable code after returns/jumps and unused temporary variables"""
        used_variables = set()
        for instr in self.program.instructions:
            if instr.arg1 and not str(instr.arg1).startswith('"'):
                used_variables.add(str(instr.arg1))
            if instr.arg2 and not str(instr.arg2).startswith('"'):
                used_variables.add(str(instr.arg2))

        new_instructions = []
        unreachable = False

        for instr in self.program.instructions:
            if instr.op == 'LABEL':
                unreachable = False

            if unreachable:
                continue

            # Eliminate unused temporary assignments (t1 = ...) if t1 is never read
            if instr.op == 'ASSIGN' and instr.result and str(instr.result).startswith('t') and str(instr.result) not in used_variables:
                continue

            new_instructions.append(instr)

            if instr.op in ('JMP', 'RET'):
                unreachable = True

        self.program.instructions = new_instructions

    def _to_number(self, val_str):
        if val_str is None:
            return None
        try:
            s = str(val_str)
            if '.' in s:
                return float(s)
            return int(s)
        except ValueError:
            return None
