import math
import statistics

# Corvus Extended Math, Trigonometry & Statistics Engine (v4.2)

class MathExtEngine:
    @staticmethod
    def sqrt(val): return math.sqrt(float(val))

    @staticmethod
    def sin(rad): return math.sin(float(rad))

    @staticmethod
    def cos(rad): return math.cos(float(rad))

    @staticmethod
    def tan(rad): return math.tan(float(rad))

    @staticmethod
    def atan2(y, x): return math.atan2(float(y), float(x))

    @staticmethod
    def radians(deg): return math.radians(float(deg))

    @staticmethod
    def degrees(rad): return math.degrees(float(rad))

    @staticmethod
    def mean(lis): return float(statistics.mean(lis))

    @staticmethod
    def median(lis): return float(statistics.median(lis))

    @staticmethod
    def variance(lis): return float(statistics.variance(lis)) if len(lis) > 1 else 0.0

    @staticmethod
    def std_dev(lis): return float(statistics.stdev(lis)) if len(lis) > 1 else 0.0

_global_math_ext_engine = MathExtEngine()
