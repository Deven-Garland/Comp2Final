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

Author: Ellie Lutz
Date:   04/12/2026
Lab:    Lab 6 - Sparse World Map
"""

import time
import random
import sys
import os

try:
    from scipy.sparse import csr_matrix
    import numpy as np
    import matplotlib.pyplot as plt
except ImportError:
    print('scipy/numpy/matplotlib not installed — run: pip install scipy numpy matplotlib')
    sys.exit(1)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datastructures.sparse_matrix import SparseMatrix

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def measure_set_time(n, size=1000):
    # Measure how long it takes to set n entries in a size x size matrix
    m = SparseMatrix(rows=size, cols=size, default=0)
    entries = [(random.randint(0, size - 1), random.randint(0, size - 1), random.randint(1, 100)) for _ in range(n)]
    start = time.perf_counter()
    for r, c, v in entries:
        m.set(r, c, v)
    end = time.perf_counter()
    return end - start, m, entries


def measure_get_time(m, entries):
    # Measure how long it takes to get each entry we just set
    start = time.perf_counter()
    for r, c, v in entries:
        m.get(r, c)
    end = time.perf_counter()
    return end - start


def measure_items_time(m):
    # Measure how long it takes to iterate over all entries
    start = time.perf_counter()
    list(m.items())
    end = time.perf_counter()
    return end - start


def measure_multiply_time(n, size=100):
    # Measure how long it takes to multiply two sparse matrices
    a = SparseMatrix(rows=size, cols=size, default=0)
    b = SparseMatrix(rows=size, cols=size, default=0)
    for _ in range(n):
        r = random.randint(0, size - 1)
        c = random.randint(0, size - 1)
        a.set(r, c, random.randint(1, 10))
        b.set(r, c, random.randint(1, 10))
    start = time.perf_counter()
    a.multiply(b)
    end = time.perf_counter()
    return end - start


def measure_scipy_set_time(n, size=1000):
    # Measure how long it takes scipy to build a sparse matrix with n entries
    rows = [random.randint(0, size - 1) for _ in range(n)]
    cols = [random.randint(0, size - 1) for _ in range(n)]
    vals = [random.randint(1, 100) for _ in range(n)]
    start = time.perf_counter()
    m = csr_matrix((vals, (rows, cols)), shape=(size, size))
    end = time.perf_counter()
    return end - start, m, list(zip(rows, cols, vals))


def measure_scipy_get_time(m, entries):
    # Measure how long it takes scipy to get each entry
    start = time.perf_counter()
    for r, c, v in entries:
        m[r, c]
    end = time.perf_counter()
    return end - start


def measure_scipy_items_time(m):
    # Measure how long it takes scipy to iterate over all entries
    start = time.perf_counter()
    cx = m.tocoo()
    list(zip(cx.row, cx.col, cx.data))
    end = time.perf_counter()
    return end - start


def save_plot(x_vals, y_vals_dict, title, x_label, y_label, filename):
    plt.figure()
    for label, y_vals in y_vals_dict.items():
        plt.plot(x_vals, y_vals, marker="o", label=label)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(True)
    plt.savefig(filename, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filename}")


def main():
    sizes = [10, 50, 100, 500, 1000]

    my_set_times = []
    my_get_times = []
    my_items_times = []
    my_mul_times = []
    scipy_set_times = []
    scipy_get_times = []
    scipy_items_times = []
    space_mine = []
    space_scipy = []

    print(f"{'n entries':<12} {'set (mine)':<15} {'set (scipy)':<15} {'get (mine)':<15} {'get (scipy)':<15} {'items (mine)':<15} {'multiply (mine)':<18}")
    print("-" * 105)

    for n in sizes:
        t_set, m, entries = measure_set_time(n)
        t_get = measure_get_time(m, entries)
        t_items = measure_items_time(m)
        t_mul = measure_multiply_time(n)

        t_scipy_set, sm, sentries = measure_scipy_set_time(n)
        t_scipy_get = measure_scipy_get_time(sm, sentries)
        t_scipy_items = measure_scipy_items_time(sm)

        my_set_times.append(t_set)
        my_get_times.append(t_get)
        my_items_times.append(t_items)
        my_mul_times.append(t_mul)
        scipy_set_times.append(t_scipy_set)
        scipy_get_times.append(t_scipy_get)
        scipy_items_times.append(t_scipy_items)

        # Space: my matrix stores 3 values per entry (row, col, value)
        # scipy CSR stores nnz values + index arrays
        space_mine.append(n * 3)
        space_scipy.append(n + n + n)  # data + indices + indptr (approx)

        print(f"{n:<12} {t_set:<15.6f} {t_scipy_set:<15.6f} {t_get:<15.6f} {t_scipy_get:<15.6f} {t_items:<15.6f} {t_mul:<18.6f}")

    print()

    # Time complexity graphs
    save_plot(
        sizes,
        {"mine": my_set_times, "scipy": scipy_set_times},
        "set() time vs n entries",
        "n entries", "time (seconds)",
        os.path.join(CURRENT_DIR, "set_complexity.png")
    )

    save_plot(
        sizes,
        {"mine": my_get_times, "scipy": scipy_get_times},
        "get() time vs n entries",
        "n entries", "time (seconds)",
        os.path.join(CURRENT_DIR, "get_complexity.png")
    )

    save_plot(
        sizes,
        {"mine": my_items_times, "scipy": scipy_items_times},
        "items() time vs n entries",
        "n entries", "time (seconds)",
        os.path.join(CURRENT_DIR, "items_complexity.png")
    )

    save_plot(
        sizes,
        {"mine": my_mul_times},
        "multiply() time vs n entries",
        "n entries", "time (seconds)",
        os.path.join(CURRENT_DIR, "multiply_complexity.png")
    )

    # Space complexity graph
    save_plot(
        sizes,
        {"mine (COO)": space_mine, "scipy (CSR)": space_scipy},
        "Space usage vs n entries",
        "n entries", "approximate values stored",
        os.path.join(CURRENT_DIR, "space_complexity.png")
    )

    print()
    print("Done! Copy the table above into analysis_write_up.md")


if __name__ == "__main__":
    main()