# Backward compatibility shim forwarding to Compiler_Windows backend
try:
    from Compiler_Windows.compiler_asm_win64 import AsmGeneratorWin64 as AsmGenerator
except ImportError:
    from compiler_asm_win64 import AsmGeneratorWin64 as AsmGenerator