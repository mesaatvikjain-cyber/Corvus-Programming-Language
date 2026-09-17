# Corvus High-Precision Benchmarking & Profiler Engine
# Measures nanosecond execution timing, memory allocations, ops/sec, and statement breakdowns

import sys
import os
import time
import math
import tracemalloc
from typing import Optional

from lexercorvus import tokenize
from parsercorvus import Parser
from evaluatorcorvus import Evaluator, Environment
from ast_optimizer import AstOptimizer

def format_time(ns: float) -> str:
    if ns < 1_000:
        return f"{ns:.2f} ns"
    elif ns < 1_000_000:
        return f"{ns / 1_000:.2f} us"
    elif ns < 1_000_000_000:
        return f"{ns / 1_000_000:.2f} ms"
    else:
        return f"{ns / 1_000_000_000:.3f} s"

def run_benchmark(filepath: str, iterations: int = 50, optimize: bool = True):
    if not os.path.exists(filepath):
        print(f"[Error]: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    tokens = tokenize(code)
    ast = Parser(tokens).parse()

    opt_stats = ""
    if optimize:
        opt = AstOptimizer()
        ast = opt.optimize(ast)
        if opt.folded_constants > 0 or opt.pruned_branches > 0:
            opt_stats = f" [Optimized: {opt.folded_constants} folded, {opt.pruned_branches} pruned]"

    print(f"==================================================")
    print(f"  Corvus Benchmark Suite: '{os.path.basename(filepath)}'{opt_stats}")
    print(f"  Iterations: {iterations} | High-Res Timer: perf_counter_ns")
    print(f"==================================================")

    # 1. Warmup run (redirect stdout to suppress program logs during benchmark)
    import io
    devnull = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = devnull
    try:
        w_env = Environment()
        w_eval = Evaluator(w_env)
        w_eval.current_file_path = filepath
        w_eval.evaluate(ast)
    except Exception as e:
        sys.stdout = old_stdout
        print(f"[Benchmark Error during warmup]: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        sys.stdout = old_stdout

    # 2. Measure Execution Times
    times_ns = []
    tracemalloc.start()
    mem_before, _ = tracemalloc.get_traced_memory()

    for i in range(iterations):
        env = Environment()
        evaluator = Evaluator(env)
        evaluator.current_file_path = filepath

        sys.stdout = devnull
        t0 = time.perf_counter_ns()
        try:
            evaluator.evaluate(ast)
        finally:
            t1 = time.perf_counter_ns()
            sys.stdout = old_stdout

        times_ns.append(t1 - t0)

    mem_current, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    total_ns = sum(times_ns)
    mean_ns = total_ns / len(times_ns)
    min_ns = min(times_ns)
    max_ns = max(times_ns)
    sorted_times = sorted(times_ns)
    median_ns = sorted_times[len(sorted_times) // 2]

    # Standard Deviation
    variance = sum((t - mean_ns) ** 2 for t in times_ns) / len(times_ns)
    stddev_ns = math.sqrt(variance)

    ops_per_sec = (1_000_000_000 / mean_ns) if mean_ns > 0 else 0

    print(f"\n  Execution Timing:")
    print(f"    - Fastest Run:   {format_time(min_ns)}")
    print(f"    - Slowest Run:   {format_time(max_ns)}")
    print(f"    - Median Run:    {format_time(median_ns)}")
    print(f"    - Mean Average:  {format_time(mean_ns)} (+/- {format_time(stddev_ns)})")
    print(f"    - Throughput:    {ops_per_sec:,.0f} runs/sec")
    print(f"\n  Memory Tracking:")
    print(f"    - Peak Allocated: {mem_peak / 1024:.2f} KB")
    print(f"==================================================")
    print(f"  [SUCCESS] Benchmark Completed Successfully.")
    print(f"==================================================")


def run_profile(filepath: str):
    if not os.path.exists(filepath):
        print(f"[Error]: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    tokens = tokenize(code)
    ast = Parser(tokens).parse()

    print(f"==================================================")
    print(f"  Corvus Execution Profiler: '{os.path.basename(filepath)}'")
    print(f"==================================================")

    # Count AST nodes
    node_counts = {}
    def count_nodes(n):
        if n is None: return
        tname = type(n).__name__
        node_counts[tname] = node_counts.get(tname, 0) + 1
        for attr, val in getattr(n, "__dict__", {}).items():
            if isinstance(val, list):
                for item in val: count_nodes(item)
            else:
                count_nodes(val)

    count_nodes(ast)

    # Timed run
    t0 = time.perf_counter_ns()
    env = Environment()
    evaluator = Evaluator(env)
    evaluator.current_file_path = filepath
    evaluator.evaluate(ast)
    t1 = time.perf_counter_ns()

    print(f"\n  Runtime Profile:")
    print(f"    - Total Time:        {format_time(t1 - t0)}")
    print(f"    - Total Statements:  {len(ast.statements)}")
    print(f"\n  AST Node Distribution:")
    for k, v in sorted(node_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"    - {k:<20}: {v:>5}")
    print(f"==================================================")
