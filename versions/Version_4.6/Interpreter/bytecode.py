# bytecode.py
# Corvus Bytecode Definitions, Instruction Set, CodeObject, Binary Serializer & Disassembler

import struct
from enum import IntEnum
from dataclasses import dataclass, field
from typing import Any, List, Optional

MAGIC_HEADER = b"CRVC\x01\x00"  # Corvus Bytecode Version 1.0

class OpCode(IntEnum):
    # Stack & Constants
    NOP = 0
    LOAD_CONST = 1      # arg: const index
    LOAD_VAR = 2        # arg: var name index
    STORE_VAR = 3       # arg: var name index
    POP = 4
    DUP = 5

    # Arithmetic & Logic
    ADD = 10
    SUB = 11
    MUL = 12
    DIV = 13
    MOD = 14
    POW = 15
    MATMUL = 16         # @ matrix multiplication
    NEG = 17
    NOT = 18

    # Comparison
    EQ = 20
    NEQ = 21
    LT = 22
    GT = 23
    LTE = 24
    GTE = 25
    IN = 26

    # Control Flow
    JUMP = 30           # arg: target instruction offset
    JUMP_IF_FALSE = 31  # arg: target instruction offset
    JUMP_IF_TRUE = 32   # arg: target instruction offset
    GET_ITER = 33       # turns TOS into an iterator
    FOR_ITER = 34       # arg: target instruction offset if exhausted; else pushes next item

    # Collections
    BUILD_LIST = 40     # arg: number of elements
    BUILD_TUPLE = 41    # arg: number of elements
    BUILD_DICT = 42     # arg: number of key-value pairs
    INDEX_GET = 43
    INDEX_SET = 44

    # Functions & Calls
    CALL_FUNC = 50      # arg: argc
    CALL_METHOD = 51    # arg: (method_name_index, argc)
    MAKE_FUNC = 52      # arg: code_object index
    RETURN = 53

    # Pattern Matching & String Interpolation
    BUILD_STRING = 60   # arg: number of parts
    HALT = 99

@dataclass
class Instruction:
    opcode: OpCode
    arg: Optional[Any] = None
    line: int = 1

    def __repr__(self):
        if self.arg is not None:
            return f"{self.opcode.name:<16} {repr(self.arg)}"
        return f"{self.opcode.name}"

@dataclass
class CodeObject:
    name: str = "<module>"
    instructions: List[Instruction] = field(default_factory=list)
    constants: List[Any] = field(default_factory=list)
    names: List[str] = field(default_factory=list)
    params: List[str] = field(default_factory=list)
    filename: str = "<memory>"

    def add_const(self, val: Any) -> int:
        for idx, c in enumerate(self.constants):
            if type(c) == type(val) and c == val:
                return idx
        self.constants.append(val)
        return len(self.constants) - 1

    def add_name(self, name: str) -> int:
        if name in self.names:
            return self.names.index(name)
        self.names.append(name)
        return len(self.names) - 1

    def emit(self, opcode: OpCode, arg: Any = None, line: int = 1) -> int:
        instr = Instruction(opcode, arg, line)
        self.instructions.append(instr)
        return len(self.instructions) - 1

    def disassemble(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}=== Disassembly of '{self.name}' ({len(self.instructions)} instructions) ==="]
        for idx, instr in enumerate(self.instructions):
            arg_str = ""
            if instr.arg is not None:
                if instr.opcode in (OpCode.LOAD_CONST,):
                    val = self.constants[instr.arg] if instr.arg < len(self.constants) else "?"
                    arg_str = f"{instr.arg} ({repr(val)})"
                elif instr.opcode in (OpCode.LOAD_VAR, OpCode.STORE_VAR):
                    val = self.names[instr.arg] if instr.arg < len(self.names) else "?"
                    arg_str = f"{instr.arg} ({val})"
                elif instr.opcode in (OpCode.JUMP, OpCode.JUMP_IF_FALSE, OpCode.JUMP_IF_TRUE):
                    arg_str = f"-> {instr.arg}"
                elif instr.opcode == OpCode.CALL_METHOD:
                    method_idx, argc = instr.arg
                    m_name = self.names[method_idx] if method_idx < len(self.names) else "?"
                    arg_str = f".{m_name}() [argc={argc}]"
                else:
                    arg_str = str(instr.arg)
            lines.append(f"{prefix}{idx:4d}  {instr.opcode.name:<16} {arg_str}")

        # Disassemble nested function code objects
        for const in self.constants:
            if isinstance(const, CodeObject):
                lines.append("")
                lines.append(const.disassemble(indent=indent + 1))
        return "\n".join(lines)

def disassemble(code_obj: CodeObject) -> str:
    return code_obj.disassemble()


def serialize(code_obj: CodeObject) -> bytes:
    buf = bytearray(MAGIC_HEADER)

    def _write_string(s: str):
        encoded = s.encode("utf-8")
        buf.extend(struct.pack("<I", len(encoded)))
        buf.extend(encoded)

    def _write_const(val: Any):
        if val is None:
            buf.append(0)
        elif isinstance(val, bool):
            buf.append(1)
            buf.append(1 if val else 0)
        elif isinstance(val, int):
            buf.append(2)
            buf.extend(struct.pack("<q", val))
        elif isinstance(val, float):
            buf.append(3)
            buf.extend(struct.pack("<d", val))
        elif isinstance(val, str):
            buf.append(4)
            _write_string(val)
        elif isinstance(val, CodeObject):
            buf.append(5)
            _write_code_object(val)
        else:
            buf.append(4)
            _write_string(str(val))

    def _write_code_object(co: CodeObject):
        _write_string(co.name)
        _write_string(co.filename)

        # Params
        buf.extend(struct.pack("<I", len(co.params)))
        for p in co.params:
            _write_string(p)

        # Names
        buf.extend(struct.pack("<I", len(co.names)))
        for name in co.names:
            _write_string(name)

        # Constants
        buf.extend(struct.pack("<I", len(co.constants)))
        for c in co.constants:
            _write_const(c)

        # Instructions
        buf.extend(struct.pack("<I", len(co.instructions)))
        for instr in co.instructions:
            buf.append(int(instr.opcode))
            buf.extend(struct.pack("<I", instr.line))
            has_arg = instr.arg is not None
            buf.append(1 if has_arg else 0)
            if has_arg:
                if isinstance(instr.arg, tuple):
                    buf.append(1) # tuple arg (e.g. CALL_METHOD)
                    buf.extend(struct.pack("<II", instr.arg[0], instr.arg[1]))
                else:
                    buf.append(0) # int arg
                    buf.extend(struct.pack("<i", int(instr.arg)))

    _write_code_object(code_obj)
    return bytes(buf)


def deserialize(data: bytes) -> CodeObject:
    if not isinstance(data, (bytes, bytearray)):
        raise ValueError("Invalid .crvc payload: Expected bytes object.")

    if not data.startswith(MAGIC_HEADER):
        raise ValueError("Invalid .crvc file: Missing or mismatched Corvus magic header.")

    offset = len(MAGIC_HEADER)
    total_len = len(data)

    def _ensure_bytes(n: int):
        if offset + n > total_len:
            raise ValueError(f"Corrupted .crvc bytecode: Unexpected EOF reading {n} bytes at offset {offset}.")

    def _read_string() -> str:
        nonlocal offset
        _ensure_bytes(4)
        length = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        if length > 10 * 1024 * 1024:  # 10MB maximum string constant sanity limit
            raise ValueError(f"Corrupted string constant: Length {length} exceeds safety limit.")
        _ensure_bytes(length)
        s = data[offset:offset + length].decode("utf-8", errors="replace")
        offset += length
        return s

    def _read_const() -> Any:
        nonlocal offset
        _ensure_bytes(1)
        tag = data[offset]
        offset += 1
        if tag == 0:
            return None
        elif tag == 1:
            _ensure_bytes(1)
            val = data[offset] == 1
            offset += 1
            return val
        elif tag == 2:
            _ensure_bytes(8)
            val = struct.unpack_from("<q", data, offset)[0]
            offset += 8
            return val
        elif tag == 3:
            _ensure_bytes(8)
            val = struct.unpack_from("<d", data, offset)[0]
            offset += 8
            return val
        elif tag == 4:
            return _read_string()
        elif tag == 5:
            return _read_code_object()
        raise ValueError(f"Unknown constant tag: {tag} at offset {offset - 1}")

    def _read_code_object() -> CodeObject:
        nonlocal offset
        name = _read_string()
        filename = _read_string()

        # Params
        _ensure_bytes(4)
        num_params = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        if num_params > 10000:
            raise ValueError(f"Corrupted .crvc file: Too many parameters ({num_params}).")
        params = [_read_string() for _ in range(num_params)]

        # Names
        _ensure_bytes(4)
        num_names = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        if num_names > 100000:
            raise ValueError(f"Corrupted .crvc file: Too many variable names ({num_names}).")
        names = [_read_string() for _ in range(num_names)]

        # Constants
        _ensure_bytes(4)
        num_constants = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        if num_constants > 100000:
            raise ValueError(f"Corrupted .crvc file: Too many constants ({num_constants}).")
        constants = [_read_const() for _ in range(num_constants)]

        # Instructions
        _ensure_bytes(4)
        num_instructions = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        if num_instructions > 1000000:
            raise ValueError(f"Corrupted .crvc file: Too many instructions ({num_instructions}).")
        instructions = []
        for _ in range(num_instructions):
            _ensure_bytes(6)
            raw_op = data[offset]
            try:
                opcode = OpCode(raw_op)
            except ValueError:
                raise ValueError(f"Corrupted .crvc file: Unknown opcode {raw_op} at offset {offset}")
            offset += 1
            line = struct.unpack_from("<I", data, offset)[0]
            offset += 4
            has_arg = data[offset] == 1
            offset += 1
            arg = None
            if has_arg:
                _ensure_bytes(1)
                arg_type = data[offset]
                offset += 1
                if arg_type == 1:
                    _ensure_bytes(8)
                    arg = struct.unpack_from("<II", data, offset)
                    offset += 8
                else:
                    _ensure_bytes(4)
                    arg = struct.unpack_from("<i", data, offset)[0]
                    offset += 4
            instructions.append(Instruction(opcode, arg, line))

        return CodeObject(
            name=name,
            instructions=instructions,
            constants=constants,
            names=names,
            params=params,
            filename=filename
        )

    return _read_code_object()
