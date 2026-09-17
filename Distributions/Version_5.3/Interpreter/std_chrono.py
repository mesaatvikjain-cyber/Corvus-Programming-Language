import time

# Corvus Chrono & Timing Module Engine (v4.2)

class ChronoEngine:
    @staticmethod
    def now():
        return time.time()

    @staticmethod
    def sleep(ms):
        time.sleep(float(ms) / 1000.0)

    @staticmethod
    def format_date(ts=None, fmt="%Y-%m-%d %H:%M:%S"):
        if ts is None:
            ts = time.time()
        return time.strftime(fmt, time.localtime(float(ts)))

_global_chrono_engine = ChronoEngine()
