import math
import random

# Corvus Native PyTorch & Autograd Deep Learning Engine (v4.2)

try:
    import torch
    HAS_NATIVE_TORCH = True
except ImportError:
    HAS_NATIVE_TORCH = False

class PyTorchEngine:
    @staticmethod
    def tensor(data, requires_grad=False):
        if HAS_NATIVE_TORCH:
            t = torch.tensor(data, dtype=torch.float32, requires_grad=requires_grad)
            return t.detach().numpy().tolist()
        return data

    @staticmethod
    def zeros(shape):
        if HAS_NATIVE_TORCH:
            return torch.zeros(shape).numpy().tolist()
        if isinstance(shape, int):
            return [0.0] * shape
        if len(shape) == 2:
            return [[0.0] * shape[1] for _ in range(shape[0])]
        return [0.0] * (shape[0] if shape else 1)

    @staticmethod
    def ones(shape):
        if HAS_NATIVE_TORCH:
            return torch.ones(shape).numpy().tolist()
        if isinstance(shape, int):
            return [1.0] * shape
        if len(shape) == 2:
            return [[1.0] * shape[1] for _ in range(shape[0])]
        return [1.0] * (shape[0] if shape else 1)

    @staticmethod
    def add(a, b):
        if HAS_NATIVE_TORCH:
            return torch.add(torch.tensor(a), torch.tensor(b)).numpy().tolist()
        if isinstance(a, list) and isinstance(b, list):
            return [x + y for x, y in zip(a, b)]
        return a + b

    @staticmethod
    def matmul(a, b):
        if HAS_NATIVE_TORCH:
            return torch.matmul(torch.tensor(a), torch.tensor(b)).numpy().tolist()
        if not isinstance(a[0], list): a = [a]
        if not isinstance(b[0], list): b = [[x] for x in b]
        result = [[0.0] * len(b[0]) for _ in range(len(a))]
        for i in range(len(a)):
            for j in range(len(b[0])):
                for k in range(len(b)):
                    result[i][j] += a[i][k] * b[k][j]
        return result

    @staticmethod
    def relu(x):
        if HAS_NATIVE_TORCH:
            return torch.relu(torch.tensor(x)).numpy().tolist()
        if isinstance(x, list):
            return [max(0.0, float(v)) for v in x]
        return max(0.0, float(x))

    @staticmethod
    def sigmoid(x):
        if HAS_NATIVE_TORCH:
            return torch.sigmoid(torch.tensor(x)).numpy().tolist()
        if isinstance(x, list):
            return [1.0 / (1.0 + math.exp(-float(v))) for v in x]
        return 1.0 / (1.0 + math.exp(-float(x)))

    @staticmethod
    def linear(inputs, in_features, out_features, weights=None, bias=None):
        if not isinstance(inputs, list):
            inputs = [inputs]
        if weights is None:
            weights = [[random.uniform(-0.1, 0.1) for _ in range(out_features)] for _ in range(in_features)]
        if bias is None:
            bias = [0.0] * out_features

        out = [0.0] * out_features
        for j in range(out_features):
            out[j] = bias[j]
            for i in range(in_features):
                out[j] += inputs[i] * weights[i][j]
        return out

    @staticmethod
    def backward(y_pred, y_true):
        # Calculates simple gradient w.r.t MSE loss
        if isinstance(y_pred, list) and isinstance(y_true, list):
            grad = [2.0 * (p - t) for p, t in zip(y_pred, y_true)]
            loss = sum((p - t) ** 2 for p, t in zip(y_pred, y_true)) / len(y_pred)
            return {"loss": loss, "grad": grad}
        loss = (y_pred - y_true) ** 2
        grad = 2.0 * (y_pred - y_true)
        return {"loss": loss, "grad": grad}

    @staticmethod
    def adam_step(params, grads, lr=0.01):
        if isinstance(params, list) and isinstance(grads, list):
            return [p - lr * g for p, g in zip(params, grads)]
        return params - lr * grads

_global_torch_engine = PyTorchEngine()
