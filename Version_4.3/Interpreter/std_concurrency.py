import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor, Future, FIRST_COMPLETED, wait

# Corvus "Murder of Crows" 🐦 Expanded Concurrency Engine (Version 4.2)

class CrowChannel:
    def __init__(self, capacity=0):
        self.q = queue.Queue(maxsize=capacity if capacity > 0 else 0)
        self._closed = False

    def send(self, value):
        if self._closed:
            raise RuntimeError("Cannot send on closed CrowChannel")
        self.q.put(value)

    def recv(self, timeout=None):
        try:
            return self.q.get(timeout=timeout)
        except queue.Empty:
            return None

    def poll(self):
        """Non-blocking poll for channel data."""
        try:
            return self.q.get_nowait()
        except queue.Empty:
            return None

    def is_empty(self):
        return self.q.empty()

    def is_full(self):
        return self.q.full()

    def close(self):
        self._closed = True


class CrowHandle:
    def __init__(self, future):
        self.future = future

    def join(self, timeout=None):
        return self.future.result(timeout=timeout)

    def done(self):
        return self.future.done()

    def cancel(self):
        return self.future.cancel()


class CrowNest:
    """Scoped Worker Pool for dedicated concurrent task sets."""
    def __init__(self, max_workers=8):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def fly(self, fn, *args):
        future = self.executor.submit(fn, *args)
        return CrowHandle(future)

    def flock(self, *crows):
        target = crows[0] if len(crows) == 1 and isinstance(crows[0], list) else crows
        results = []
        for crow in target:
            if isinstance(crow, CrowHandle):
                results.append(crow.join())
            elif hasattr(crow, 'join'):
                results.append(crow.join())
            else:
                results.append(crow)
        return results

    def shutdown(self):
        self.executor.shutdown(wait=False)


class CrowEngine:
    def __init__(self, max_workers=32):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def fly(self, fn, *args):
        future = self.executor.submit(fn, *args)
        return CrowHandle(future)

    def flock(self, *crows):
        target = crows[0] if len(crows) == 1 and isinstance(crows[0], list) else crows
        results = []
        for crow in target:
            if isinstance(crow, CrowHandle):
                results.append(crow.join())
            elif hasattr(crow, 'join'):
                results.append(crow.join())
            else:
                results.append(crow)
        return results

    def channel(self, capacity=0):
        return CrowChannel(capacity=capacity)

    def nest(self, max_workers=8):
        return CrowNest(max_workers=max_workers)

    def race(self, *crows):
        """Returns the result of the FIRST crow to complete."""
        target = crows[0] if len(crows) == 1 and isinstance(crows[0], list) else crows
        futures_map = {}
        for crow in target:
            if isinstance(crow, CrowHandle):
                futures_map[crow.future] = crow
            elif isinstance(crow, Future):
                futures_map[crow] = crow

        if not futures_map:
            return None

        done_set, _ = wait(futures_map.keys(), return_when=FIRST_COMPLETED)
        fastest_future = next(iter(done_set))
        return fastest_future.result()

    def select(self, *channels):
        """Waits on multiple channels, returning (channel_index, value) for the first with data."""
        target = channels[0] if len(channels) == 1 and isinstance(channels[0], list) else channels
        while True:
            for idx, ch in enumerate(target):
                if isinstance(ch, CrowChannel):
                    val = ch.poll()
                    if val is not None:
                        return [idx, val]
            time.sleep(0.001)

    def parallel_map(self, fn, items):
        """Applies fn concurrently across items list and returns ordered results."""
        if not items:
            return []
        futures = [self.executor.submit(fn, item) for item in items]
        return [f.result() for f in futures]

    def ticker(self, interval_sec):
        """Emits periodic ticks onto a CrowChannel at interval_sec."""
        ch = CrowChannel()
        def _tick_loop():
            while not ch._closed:
                time.sleep(interval_sec)
                if ch._closed: break
                try:
                    ch.send(time.time())
                except Exception:
                    break
        self.executor.submit(_tick_loop)
        return ch


_global_crow_engine = CrowEngine()
