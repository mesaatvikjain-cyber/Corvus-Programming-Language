import math
import random

# Corvus Native TensorFlow & Keras Deep Learning Engine (v4.2)

try:
    import tensorflow as tf
    HAS_NATIVE_TF = True
except ImportError:
    HAS_NATIVE_TF = False

class TensorFlowEngine:
    @staticmethod
    def tensor(data):
        if HAS_NATIVE_TF:
            return tf.constant(data).numpy().tolist()
        return data

    @staticmethod
    def zeros(shape):
        if HAS_NATIVE_TF:
            return tf.zeros(shape).numpy().tolist()
        if isinstance(shape, int):
            return [0.0] * shape
        if len(shape) == 2:
            return [[0.0] * shape[1] for _ in range(shape[0])]
        return [0.0] * (shape[0] if shape else 1)

    @staticmethod
    def ones(shape):
        if HAS_NATIVE_TF:
            return tf.ones(shape).numpy().tolist()
        if isinstance(shape, int):
            return [1.0] * shape
        if len(shape) == 2:
            return [[1.0] * shape[1] for _ in range(shape[0])]
        return [1.0] * (shape[0] if shape else 1)

    @staticmethod
    def add(a, b):
        if HAS_NATIVE_TF:
            return tf.add(a, b).numpy().tolist()
        if isinstance(a, list) and isinstance(b, list):
            return [x + y for x, y in zip(a, b)]
        return a + b

    @staticmethod
    def matmul(a, b):
        if HAS_NATIVE_TF:
            return tf.matmul(a, b).numpy().tolist()
        # Fallback 2D matrix multiplication
        rows_a = len(a)
        cols_a = len(a[0]) if isinstance(a[0], list) else 1
        cols_b = len(b[0]) if isinstance(b[0], list) else 1
        
        if not isinstance(a[0], list):
            a = [a]
        if not isinstance(b[0], list):
            b = [[x] for x in b]

        result = [[0.0] * len(b[0]) for _ in range(len(a))]
        for i in range(len(a)):
            for j in range(len(b[0])):
                for k in range(len(b)):
                    result[i][j] += a[i][k] * b[k][j]
        return result

    @staticmethod
    def relu(x):
        if HAS_NATIVE_TF:
            return tf.nn.relu(x).numpy().tolist()
        if isinstance(x, list):
            return [max(0.0, float(v)) for v in x]
        return max(0.0, float(x))

    @staticmethod
    def sigmoid(x):
        if HAS_NATIVE_TF:
            return tf.nn.sigmoid(x).numpy().tolist()
        if isinstance(x, list):
            return [1.0 / (1.0 + math.exp(-float(v))) for v in x]
        return 1.0 / (1.0 + math.exp(-float(x)))

    @staticmethod
    def softmax(x):
        if HAS_NATIVE_TF:
            return tf.nn.softmax(x).numpy().tolist()
        if isinstance(x, list):
            exps = [math.exp(float(v)) for v in x]
            s = sum(exps) or 1.0
            return [e / s for e in exps]
        return 1.0

    @staticmethod
    def dense(inputs, units, weights=None, bias=None):
        if not isinstance(inputs, list):
            inputs = [inputs]
        in_dim = len(inputs)
        if weights is None:
            weights = [[random.uniform(-0.5, 0.5) for _ in range(units)] for _ in range(in_dim)]
        if bias is None:
            bias = [0.0] * units

        outputs = [0.0] * units
        for j in range(units):
            outputs[j] = bias[j]
            for i in range(in_dim):
                outputs[j] += inputs[i] * weights[i][j]
        return outputs

    @staticmethod
    def predict(model_weights, inputs):
        curr = inputs
        for layer in model_weights:
            curr = TensorFlowEngine.dense(curr, layer.get("units", 1), layer.get("weights"), layer.get("bias"))
            act = layer.get("activation", "none")
            if act == "relu":
                curr = TensorFlowEngine.relu(curr)
            elif act == "sigmoid":
                curr = TensorFlowEngine.sigmoid(curr)
            elif act == "softmax":
                curr = TensorFlowEngine.softmax(curr)
        return curr

_global_tf_engine = TensorFlowEngine()
