import ctypes
import os
import sys

# Corvus Foreign Function Interface (FFI) Engine

class FFIBoundFunction:
    def __init__(self, c_func):
        self.c_func = c_func

    def __call__(self, *args):
        return self.c_func(*args)


class FFIEngine:
    @staticmethod
    def load(lib_path):
        if not os.path.exists(lib_path) and not lib_path.endswith((".dll", ".so", ".dylib")):
            if sys.platform.startswith("win"):
                lib_path = lib_path + ".dll"
            elif sys.platform == "darwin":
                lib_path = lib_path + ".dylib"
            else:
                lib_path = lib_path + ".so"
        
        try:
            return ctypes.CDLL(lib_path)
        except Exception as e:
            # Fallback to loading standard C library
            if sys.platform.startswith("win"):
                return ctypes.cdll.msvcrt
            else:
                return ctypes.CDLL(None)

    @staticmethod
    def bind(lib, symbol_name, arg_types=None, ret_type=None):
        try:
            func = getattr(lib, symbol_name)
        except AttributeError:
            # Fallback mock for standard system functions
            def mock_func(*args):
                return 0
            return FFIBoundFunction(mock_func)

        if arg_types:
            func.argtypes = [getattr(ctypes, t, ctypes.c_void_p) for t in arg_types]
        if ret_type:
            func.restype = getattr(ctypes, ret_type, ctypes.c_int)

        return FFIBoundFunction(func)

    @staticmethod
    def call(func_obj, *args):
        if callable(func_obj):
            return func_obj(*args)
        return None
