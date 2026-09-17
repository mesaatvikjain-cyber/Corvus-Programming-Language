import math

# Corvus Native NumPy Array & Matrix Math Engine (v4.2)

try:
    import numpy as np
    HAS_NATIVE_NUMPY = True
except ImportError:
    HAS_NATIVE_NUMPY = False

class NumPyEngine:
    @staticmethod
    def array(data):
        if HAS_NATIVE_NUMPY:
            return np.array(data).tolist()
        return data

    @staticmethod
    def zeros(shape):
        if HAS_NATIVE_NUMPY:
            return np.zeros(shape).tolist()
        if isinstance(shape, int):
            return [0.0] * shape
        if len(shape) == 2:
            return [[0.0] * shape[1] for _ in range(shape[0])]
        return [0.0]

    @staticmethod
    def ones(shape):
        if HAS_NATIVE_NUMPY:
            return np.ones(shape).tolist()
        if isinstance(shape, int):
            return [1.0] * shape
        if len(shape) == 2:
            return [[1.0] * shape[1] for _ in range(shape[0])]
        return [1.0]

    @staticmethod
    def dot(a, b):
        if HAS_NATIVE_NUMPY:
            return np.dot(a, b).tolist()
        if isinstance(a, list) and isinstance(b, list):
            if not isinstance(a[0], list) and not isinstance(b[0], list):
                return sum(x * y for x, y in zip(a, b))
        return a

    @staticmethod
    def transpose(matrix):
        if HAS_NATIVE_NUMPY:
            return np.transpose(matrix).tolist()
        if isinstance(matrix, list) and isinstance(matrix[0], list):
            return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]
        return matrix

    @staticmethod
    def sum(lis):
        if HAS_NATIVE_NUMPY:
            return float(np.sum(lis))
        if isinstance(lis, list):
            return float(sum(lis))
        return float(lis)

    @staticmethod
    def mean(lis):
        if HAS_NATIVE_NUMPY:
            return float(np.mean(lis))
        if isinstance(lis, list) and len(lis) > 0:
            return sum(lis) / len(lis)
        return 0.0

    @staticmethod
    def std(lis):
        if HAS_NATIVE_NUMPY:
            return float(np.std(lis))
        if isinstance(lis, list) and len(lis) > 0:
            m = sum(lis) / len(lis)
            var = sum((x - m) ** 2 for x in lis) / len(lis)
            return math.sqrt(var)
        return 0.0

_global_numpy_engine = NumPyEngine()
