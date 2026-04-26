"""
sparse_matrix_complexity.py - Performance analysis for SparseMatrix

Compare your SparseMatrix implementation to:
  - scipy.sparse (CSR format)
  - numpy dense matrix (numpy.ndarray)

Run with:
    cd code/game/datastructures/complexity
    python sparse_matrix_complexity.py

Install dependencies if needed:
    pip install scipy numpy

Author: [Deven Garland]
Date:   [4/11/2026]
Lab:    Lab 6 - Sparse World Map
"""

import time
import random
import sys
import os
import tracemalloc

try:
    from scipy.sparse import csr_matrix
    import numpy as np
except ImportError:
    print('error: scipy/numpy not installed — run: pip install scipy numpy')
    sys.exit(1)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from datastructures.sparse_matrix import SparseMatrix

SIZE     = 500
DENSITY  = 0.01
NUM_GETS = 1000


def generate_entries():
    entries = []
    for _ in range(int(SIZE * SIZE * DENSITY)):
        r = random.randint(0, SIZE - 1)
        c = random.randint(0, SIZE - 1)
        v = random.randint(1, 100)
        entries.append((r, c, v))
    return entries


def run_benchmark(entries):
    print("=== Time Benchmark ===")
    print(f"Matrix size: {SIZE}x{SIZE}, density: {DENSITY*100}%, entries: {len(entries)}\n")

    # ----------------------------------------------------------------
    # SparseMatrix
    # ----------------------------------------------------------------
    t0 = time.time()
    m = SparseMatrix(default=0)
    for r, c, v in entries:
        m.set(r, c, v)
    t1 = time.time()
    sparse_build = t1 - t0
    print(f"SparseMatrix  build:    {sparse_build:.4f}s  ({len(m)} entries stored)")

    t0 = time.time()
    for _ in range(NUM_GETS):
        m.get(random.randint(0, SIZE-1), random.randint(0, SIZE-1))
    t1 = time.time()
    sparse_get = t1 - t0
    print(f"SparseMatrix  get:      {sparse_get:.4f}s  ({NUM_GETS} accesses)")

    t0 = time.time()
    list(m.items())
    t1 = time.time()
    sparse_items = t1 - t0
    print(f"SparseMatrix  items:    {sparse_items:.4f}s")

    # Multiply two small sparse matrices
    A = SparseMatrix(default=0)
    B = SparseMatrix(default=0)
    for i in range(50):
        A.set(random.randint(0,49), random.randint(0,49), random.randint(1,10))
        B.set(random.randint(0,49), random.randint(0,49), random.randint(1,10))
    t0 = time.time()
    A.multiply(B)
    t1 = time.time()
    sparse_mul = t1 - t0
    print(f"SparseMatrix  multiply: {sparse_mul:.4f}s  (50x50 matrices)")

    print()

    # ----------------------------------------------------------------
    # scipy
    # ----------------------------------------------------------------
    rows, cols, vals = zip(*entries) if entries else ([], [], [])

    t0 = time.time()
    sci = csr_matrix((vals, (rows, cols)), shape=(SIZE, SIZE))
    t1 = time.time()
    scipy_build = t1 - t0
    print(f"scipy         build:    {scipy_build:.4f}s")

    t0 = time.time()
    for _ in range(NUM_GETS):
        sci[random.randint(0, SIZE-1), random.randint(0, SIZE-1)]
    t1 = time.time()
    scipy_get = t1 - t0
    print(f"scipy         get:      {scipy_get:.4f}s  ({NUM_GETS} accesses)")

    t0 = time.time()
    cx = sci.tocoo()
    list(zip(cx.row, cx.col, cx.data))
    t1 = time.time()
    scipy_items = t1 - t0
    print(f"scipy         items:    {scipy_items:.4f}s")

    A_sci = csr_matrix(np.random.randint(0, 2, (50, 50)))
    B_sci = csr_matrix(np.random.randint(0, 2, (50, 50)))
    t0 = time.time()
    A_sci.dot(B_sci)
    t1 = time.time()
    scipy_mul = t1 - t0
    print(f"scipy         multiply: {scipy_mul:.4f}s  (50x50 matrices)")

    print()

    # ----------------------------------------------------------------
    # numpy dense
    # ----------------------------------------------------------------
    t0 = time.time()
    dense = np.zeros((SIZE, SIZE))
    for r, c, v in entries:
        dense[r][c] = v
    t1 = time.time()
    numpy_build = t1 - t0
    print(f"numpy         build:    {numpy_build:.4f}s")

    t0 = time.time()
    for _ in range(NUM_GETS):
        dense[random.randint(0, SIZE-1), random.randint(0, SIZE-1)]
    t1 = time.time()
    numpy_get = t1 - t0
    print(f"numpy         get:      {numpy_get:.4f}s  ({NUM_GETS} accesses)")

    t0 = time.time()
    for r in range(SIZE):
        for c in range(SIZE):
            _ = dense[r][c]
    t1 = time.time()
    numpy_items = t1 - t0
    print(f"numpy         items:    {numpy_items:.4f}s  (full iteration)")

    A_np = np.random.randint(0, 2, (50, 50))
    B_np = np.random.randint(0, 2, (50, 50))
    t0 = time.time()
    np.dot(A_np, B_np)
    t1 = time.time()
    numpy_mul = t1 - t0
    print(f"numpy         multiply: {numpy_mul:.4f}s  (50x50 matrices)")

    print()
    print("=== Summary Table ===")
    print(f"{'Operation':<20} {'SparseMatrix':>15} {'scipy':>15} {'numpy':>15}")
    print("-" * 65)
    print(f"{'build':<20} {sparse_build:>14.4f}s {scipy_build:>14.4f}s {numpy_build:>14.4f}s")
    print(f"{'get':<20} {sparse_get:>14.4f}s {scipy_get:>14.4f}s {numpy_get:>14.4f}s")
    print(f"{'items':<20} {sparse_items:>14.4f}s {scipy_items:>14.4f}s {numpy_items:>14.4f}s")
    print(f"{'multiply':<20} {sparse_mul:>14.4f}s {scipy_mul:>14.4f}s {numpy_mul:>14.4f}s")


def measure_memory(entries):
    print("\n=== Memory Usage ===")

    # SparseMatrix
    tracemalloc.start()
    m = SparseMatrix(default=0)
    for r, c, v in entries:
        m.set(r, c, v)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"SparseMatrix  memory:   current={current/1024:.2f}KB  peak={peak/1024:.2f}KB")

    # scipy
    rows, cols, vals = zip(*entries) if entries else ([], [], [])
    tracemalloc.start()
    sci = csr_matrix((vals, (rows, cols)), shape=(SIZE, SIZE))
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"scipy         memory:   current={current/1024:.2f}KB  peak={peak/1024:.2f}KB")

    # numpy
    tracemalloc.start()
    dense = np.zeros((SIZE, SIZE))
    for r, c, v in entries:
        dense[r][c] = v
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    numpy_bytes = SIZE * SIZE * 8
    print(f"numpy         memory:   current={current/1024:.2f}KB  peak={peak/1024:.2f}KB")
    print(f"numpy         theoretical: {numpy_bytes/1024:.2f}KB  ({SIZE}x{SIZE}x8 bytes)")




if __name__ == '__main__':
    random.seed(42)
    entries = generate_entries()
    run_benchmark(entries)
    measure_memory(entries)