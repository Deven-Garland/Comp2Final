"""
sparse_matrix_complexity.py - Performance analysis for SparseMatrix

Compare your SparseMatrix implementation to:
  - scipy.sparse (CSR format)
  - numpy dense matrix (numpy.ndarray)

Measure and report wall-clock time for:
  1. Building the matrix (set() calls)
  2. Random get() accesses
  3. items() full iteration
  4. multiply()

Run with:
    cd code/game/datastructures/complexity
    python sparse_matrix_complexity.py

Install dependencies if needed:
    pip install scipy numpy

Author: Mennah Khaled Dewidar
Date:   4/12/2026
Lab:    Lab 6 - Sparse World Map
"""

import time
import random
import sys
import os

try:
    from scipy.sparse import csr_matrix
    import numpy as np
except ImportError:
    print("scipy/numpy not installed — run: pip install scipy numpy")
    sys.exit(1)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datastructures.sparse_matrix import SparseMatrix

# building my SparseMatrix implementation

def build_sparse(n):
    m = SparseMatrix(default=0)
    for i in range(n):
        m.set(i, i, i + 1)
    return m

# building scipy.sparse (CSR format)

def build_csr(n):
    data = [i + 1 for i in range(n)]
    rows = [i for i in range(n)]
    cols = [i for i in range(n)]
    return csr_matrix((data, (rows, cols)), shape=(n, n))

# building numpy dense matrix (numpy.ndarray)

def build_numpy(n):
    arr = np.zeros((n, n))
    for i in range(n):
        arr[i][i] = i + 1
    return arr

sizes = [100, 500, 1000]

# Building the matrix (set() calls)
for n in sizes:
    start = time.perf_counter()
    m = build_sparse(n)
    sparse_time = time.perf_counter() - start

    start = time.perf_counter()
    csr = build_csr(n)
    csr_time = time.perf_counter() - start

    start = time.perf_counter()
    arr = build_numpy(n)
    numpy_time = time.perf_counter() - start

    print(f"Time comparison of building the matrix ... set()")
    print(f"n={n}: Sparse={sparse_time:.6f}s | CSR={csr_time:.6f}s | NumPy={numpy_time:.6f}s")

# Random get() accesses
for n in sizes:
    m = build_sparse(n)
    csr = build_csr(n)
    arr = build_numpy(n)

    indices = [random.randint(0, n - 1) for _ in range(n)]

    start = time.perf_counter()
    for i in indices:
        m.get(i, i)
    sparse_time = time.perf_counter() - start

    start = time.perf_counter()
    for i in indices:
        csr[i, i]
    csr_time = time.perf_counter() - start

    start = time.perf_counter()
    for i in indices:
        arr[i][i]
    numpy_time = time.perf_counter() - start

    print(f"Time comparison of random get() accesses")
    print(f"n={n}: Sparse={sparse_time:.6f}s | CSR={csr_time:.6f}s | NumPy={numpy_time:.6f}s")

# items() full iteration
for n in sizes:
    m = build_sparse(n)
    csr = build_csr(n)
    arr = build_numpy(n)

    start = time.perf_counter()
    for items in m.items():
        pass
    sparse_time = time.perf_counter() - start

    start = time.perf_counter()
    csr.nonzero()
    csr_time = time.perf_counter() - start

    start = time.perf_counter()
    for i in range(n):
        for j in range(n):
            items = arr[i][j]
    numpy_time = time.perf_counter() - start

    print(f"Time comparison of items() full iteration")
    print(f"n={n}: Sparse={sparse_time:.6f}s | CSR={csr_time:.6f}s | NumPy={numpy_time:.6f}s")

# multiply()
for n in sizes:
    m1 = build_sparse(n)
    m2 = build_sparse(n)

    csr1 = build_csr(n)
    csr2 = build_csr(n)

    arr1 = build_numpy(n)
    arr2 = build_numpy(n)

    start = time.perf_counter()
    m1.multiply(m2)
    sparse_time = time.perf_counter() - start

    start = time.perf_counter()
    csr1.dot(csr2)
    csr_time = time.perf_counter() - start

    start = time.perf_counter()
    np.dot(arr1, arr2)
    numpy_time = time.perf_counter() - start

    print(f"Time comparison of multiply()")
    print(f"n={n}: Sparse={sparse_time:.6f}s | CSR={csr_time:.6f}s | NumPy={numpy_time:.6f}s")
