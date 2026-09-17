# std_channel.py
# Corvus Native Async Channels & Message Passing
# Provides Go / Rust style thread-safe typed channels for concurrency.

import queue
from typing import Any, Optional

class CorvusChannel:
    """Thread-safe FIFO channel for concurrent Corvus tasks."""
    def __init__(self, capacity: int = 0):
        self.capacity = capacity
        # 0 means unbounded queue in Python queue.Queue
        self._q = queue.Queue(maxsize=capacity if capacity > 0 else 0)
        self._closed = False

    def send(self, item: Any) -> bool:
        """Send an item into the channel. Returns False if channel is closed."""
        if self._closed:
            raise RuntimeError("Cannot send on closed Corvus channel.")
        self._q.put(item)
        return True

    def recv(self, timeout: Optional[float] = None) -> Any:
        """Receive an item from the channel, blocking until available."""
        if self._closed and self._q.empty():
            return None
        try:
            return self._q.get(block=True, timeout=timeout)
        except queue.Empty:
            return None

    def try_recv(self) -> Any:
        """Non-blocking receive. Returns None if channel is currently empty."""
        try:
            return self._q.get_nowait()
        except queue.Empty:
            return None

    def close(self):
        """Close the channel."""
        self._closed = True

    def is_closed(self) -> bool:
        return self._closed

    def is_empty(self) -> bool:
        return self._q.empty()

    def is_full(self) -> bool:
        return self._q.full()

    def size(self) -> int:
        return self._q.qsize()

    def __len__(self) -> int:
        return self._q.qsize()

    def __repr__(self) -> str:
        status = "closed" if self._closed else "open"
        return f"<CorvusChannel capacity={self.capacity} size={self._q.qsize()} status={status}>"


def channel_new(capacity: int = 0) -> CorvusChannel:
    return CorvusChannel(capacity=capacity)
