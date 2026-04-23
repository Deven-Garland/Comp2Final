# Sparse Matrix Complexity Analysis

**Name:** Ellie Lutz
**Date:** 04/12/2026
**Implementation:** COO (Coordinate List)

---

## Overview

I chose Option B (COO — Coordinate List) because it was the simplest to implement
using my existing ArrayList from Lab 3. Each non-default entry is stored as a
(row, col, value) tuple in an ArrayList. This is appropriate for the tile-map use
case because most tiles share the same default value (-1), so only a small fraction
of entries need to be stored. The main trade-off is that get() and set() require
a linear scan through all stored entries (O(nnz)), whereas scipy's CSR format uses
index arrays that allow faster lookup.

---

## Time Complexity

Fill in the `?` cells after analysing your implementation.

| Operation | Your SparseMatrix | scipy sparse (CSR) | numpy dense |
|-----------|-------------------|--------------------|-------------|
| `set(r, c, v)` | O(nnz) | O(nnz) amortised | O(1) |
| `get(r, c)` | O(nnz) | O(log nnz) | O(1) |
| `items()` iteration | O(nnz) | O(nnz) | O(n²) |
| `multiply(other)` | O(nnz²) | O(nnz²/n) | O(n³) |

*nnz = number of non-zero entries, n = matrix dimension side length*

- **set**: My implementation scans the entire ArrayList to check if the entry already exists, so it is O(nnz).
- **get**: Same as set — requires a linear scan through all stored entries to find a match.
- **items**: Simply iterates through the ArrayList once, so it is O(nnz).
- **multiply**: For each entry in A, scans all entries in B looking for a column match, giving O(nnz²).

---

## Benchmark Results
gizmo[5]: python sparse_matrix_complexity.py 
n entries    set (mine)      set (scipy)     get (mine)      get (scipy)     items (mine)    multiply (mine)   
---------------------------------------------------------------------------------------------------------
10           0.000038        0.000566        0.000024        0.000398        0.000167        0.000041          
50           0.000226        0.000394        0.000217        0.001360        0.000049        0.000831          
100          0.001015        0.000510        0.001098        0.002527        0.000112        0.004643          
500          0.019739        0.000901        0.021773        0.013183        0.000506        0.903650          
1000         0.083338        0.000953        0.079415        0.024681        0.001165        8.804209          

---

## Space Complexity

| Representation | Space Used |
|----------------|-----------|
| Dense n×n      | O(n²)     |
| My sparse    | O(nnz)    |

My COO implementation stores exactly 3 values per non-zero entry (row, col, value),
so space is O(nnz). A dense matrix stores every cell regardless of value, so it uses
O(n²) space. My sparse matrix uses more memory than a dense matrix when nnz > n²/3,
meaning when more than about 33% of entries are non-default.

---

## Observations

1. My implementation is significantly slower than scipy for large n — at n=1000, my set() takes 0.083s vs scipy's 0.001s. This is because scipy uses optimized C code internally.
2. A sparse representation is faster than a dense one when most entries are the default value — for a tile map where most tiles are empty (-1), this saves a lot of memory.
3. The overhead per entry is very noticeable at larger sizes — the linear scan for get() and set() becomes very slow compared to scipy's indexed lookup.

---

## Conclusions

Sparse matrices are a powerful tool when data is mostly uniform with only a few
important entries, like a tile map. My COO implementation is simple and correct
but slow for large inputs due to its O(nnz) linear scan for every get and set. A
production implementation like scipy's CSR format uses smarter indexing to achieve
much better performance, showing that data structure choice has a huge impact on
real-world speed.

---

## References

- scipy.sparse documentation: https://docs.scipy.org/doc/scipy/reference/sparse.html
- Lab 6 instructions