import threading
import queue
from concurrent.futures import ThreadPoolExecutor

# Corvus "Murder of Crows" 🐦 Concurrency Engine

class CrowChannel:
    def __init__(self):
        self.q = queue.Queue()

    def send(self, value):
        self.q.put(value)

    def recv(self):
        return self.q.get()


class CrowHandle:
    def __init__(self, future):
        self.future = future

    def join(self):
        return self.future.result()


class CrowEngine:
    def __init__(self, max_workers=16):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def fly(self, fn, *args):
        future = self.executor.submit(fn, *args)
        return CrowHandle(future)

    def flock(self, *crows):
        results = []
        target_crows = crows[0] if len(crows) == 1 and isinstance(crows[0], list) else crows
        for crow in target_crows:
            if isinstance(crow, CrowHandle):
                results.append(crow.join())
            elif hasattr(crow, 'join'):
                results.append(crow.join())
            else:
                results.append(crow)
        return results

    def channel(self):
        return CrowChannel()

_global_crow_engine = CrowEngine()
