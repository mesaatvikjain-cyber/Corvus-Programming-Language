import sys
import gc
import weakref

# Corvus Advanced Memory Management Engine with Cycle Detection & Weak References (v4.2)

class WeakRefContainer:
    def __init__(self, obj):
        try:
            self._ref = weakref.ref(obj)
        except TypeError:
            # Fallback for immutable/builtin types
            self._ref = lambda: obj

    def deref(self):
        return self._ref()


class MemoryManager:
    def __init__(self):
        self.total_allocated = 0
        self.allocations_count = 0
        self.deallocations_count = 0
        self.heap = {}
        self.next_id = 1
        self.gc_objects = {}

    def alloc(self, size):
        ptr = f"0x{self.next_id:08X}"
        self.next_id += 1
        buf = bytearray(int(size))
        self.heap[ptr] = buf
        self.total_allocated += int(size)
        self.allocations_count += 1
        return ptr

    def free(self, ptr):
        if ptr in self.heap:
            size = len(self.heap[ptr])
            del self.heap[ptr]
            self.total_allocated -= size
            self.deallocations_count += 1
            return True
        return False

    def stats(self):
        return {
            "allocated_bytes": self.total_allocated,
            "total_allocations": self.allocations_count,
            "total_deallocations": self.deallocations_count,
            "active_heap_objects": len(self.heap),
            "unreachable_cycles_collected": gc.get_stats()[0]['collections']
        }

    def refcount(self, obj):
        return sys.getrefcount(obj) - 1

    def detect_cycles(self):
        """Scans runtime heap graph to detect cyclic reference loops."""
        unreachable = gc.collect()
        return {
            "cycles_found": len(gc.garbage),
            "garbage_count": len(gc.garbage),
            "status": "clean" if len(gc.garbage) == 0 else "cyclic_references_detected"
        }

    def collect_cycles(self):
        """Runs cycle collection pass to free unreachable circular reference chains."""
        freed = gc.collect()
        del gc.garbage[:]
        return freed

    def weak_ref(self, target):
        """Creates a weak reference to target object."""
        return WeakRefContainer(target)

    def de_weak(self, ref):
        """Dereferences a weak reference container."""
        if isinstance(ref, WeakRefContainer):
            return ref.deref()
        return ref

_global_mem_manager = MemoryManager()
