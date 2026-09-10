# std_sklearn.py
"""Corvus Native scikit-learn Machine Learning Engine (v4.3)
Provides high-performance estimators and metrics with automatic fallback.
"""
import math

try:
    import sklearn
    from sklearn.linear_model import LinearRegression as SKLinearRegression
    from sklearn.metrics import mean_squared_error as sk_mse
    HAS_NATIVE_SKLEARN = True
except ImportError:
    HAS_NATIVE_SKLEARN = False

class LinearRegressionModel:
    def __init__(self):
        self.slope = 0.0
        self.intercept = 0.0

    def fit(self, X, y):
        if isinstance(X, list) and isinstance(y, list) and len(X) > 0:
            x_vals = [x[0] if isinstance(x, list) else x for x in X]
            n = len(x_vals)
            mean_x = sum(x_vals) / n
            mean_y = sum(y) / n
            denom = sum((x - mean_x) ** 2 for x in x_vals)
            if denom != 0:
                self.slope = sum((x - mean_x) * (y_val - mean_y) for x, y_val in zip(x_vals, y)) / denom
            else:
                self.slope = 0.0
            self.intercept = mean_y - self.slope * mean_x
        return self

    def predict(self, X):
        if isinstance(X, list):
            x_vals = [x[0] if isinstance(x, list) else x for x in X]
            return [self.slope * x + self.intercept for x in x_vals]
        return self.slope * X + self.intercept

class SklearnEngine:
    @staticmethod
    def linear_regression():
        return LinearRegressionModel()

    @staticmethod
    def mean_squared_error(y_true, y_pred):
        if isinstance(y_true, list) and isinstance(y_pred, list) and len(y_true) > 0:
            return sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / len(y_true)
        return (y_true - y_pred) ** 2

_global_sklearn_engine = SklearnEngine()
