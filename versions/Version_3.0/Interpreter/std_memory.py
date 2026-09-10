import sys

# Corvus Memory Management Engine (std_memory)

class MemoryManager:
    def __init__(self):
        self.total_allocated = 0
        self.allocations_count = 0
        self.deallocations_count = 0
        self.heap = {}
        self.next_id = 1

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
            "active_objects": len(self.heap)
        }

    def refcount(self, obj):
        return sys.getrefcount(obj) - 1

_global_mem_manager = MemoryManager()
