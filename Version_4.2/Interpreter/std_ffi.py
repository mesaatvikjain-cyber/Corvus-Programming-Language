import ctypes
import ctypes.util
import os
import sys

# Corvus Foreign Function Interface (FFI) Engine (v4.2)

TYPE_MAP = {
    "int": ctypes.c_int,
    "float": ctypes.c_double,
    "double": ctypes.c_double,
    "string": ctypes.c_char_p,
    "str": ctypes.c_char_p,
    "void": None,
    "pointer": ctypes.c_void_p,
    "bool": ctypes.c_bool
}

class FFIBoundFunction:
    def __init__(self, c_func, arg_types=None, ret_type=None):
        self.c_func = c_func
        self.arg_types = arg_types or []
        self.ret_type = ret_type

    def __call__(self, *args):
        converted_args = []
        for arg, t_name in zip(args, self.arg_types if self.arg_types else [None]*len(args)):
            if isinstance(arg, str) and t_name in ("string", "str"):
                converted_args.append(arg.encode('utf-8'))
            else:
                converted_args.append(arg)

        res = self.c_func(*converted_args)

        if isinstance(res, bytes):
            return res.decode('utf-8', errors='replace')
        return res


class FFIEngine:
    @staticmethod
    def load(lib_name_or_path):
        if not lib_name_or_path:
            lib_name_or_path = ctypes.util.find_library("c") or ("msvcrt" if sys.platform.startswith("win") else "c")

        if os.path.exists(lib_name_or_path):
            try:
                return ctypes.CDLL(lib_name_or_path)
            except Exception:
                pass

        resolved = ctypes.util.find_library(lib_name_or_path)
        if resolved:
            try:
                return ctypes.CDLL(resolved)
            except Exception:
                pass

        try:
            return ctypes.CDLL(lib_name_or_path)
        except Exception:
            if sys.platform.startswith("win"):
                return ctypes.cdll.msvcrt
            else:
                return ctypes.CDLL(None)

    @staticmethod
    def bind(lib, symbol_name, arg_types=None, ret_type="int"):
        try:
            func = getattr(lib, symbol_name)
        except AttributeError:
            def _fallback(*args):
                return 0
            return FFIBoundFunction(_fallback, arg_types, ret_type)

        c_argtypes = []
        if arg_types:
            for t in arg_types:
                c_argtypes.append(TYPE_MAP.get(str(t).lower(), ctypes.c_void_p))
            func.argtypes = c_argtypes

        if ret_type:
            func.restype = TYPE_MAP.get(str(ret_type).lower(), ctypes.c_int)

        return FFIBoundFunction(func, arg_types, ret_type)

    @staticmethod
    def call(func_obj, *args):
        if callable(func_obj):
            return func_obj(*args)
        return None

_global_ffi_engine = FFIEngine()
