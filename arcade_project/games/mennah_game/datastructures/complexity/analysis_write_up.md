# Sparse Matrix Complexity Analysis

**Name:** Mennah Khaled Dewidar
**Date:** 4/12/2026
**Implementation:** [DOK / COO / CSR — circle one]

---

## Overview

Describe your implementation choice and why you chose it.  For example:
- What backing data structure does it use?
- Why is it appropriate for the tile-map use case?
- What trade-offs does it make compared to the other options?

---

## Time Complexity

Fill in the `?` cells after analysing your implementation.

| Operation | Your SparseMatrix | scipy sparse (CSR) | numpy dense |
|-----------|-------------------|--------------------|-------------|
| `set(r, c, v)` | O(nnz) | O(nnz) amortised | O(1) |
| `get(r, c)` | O(nnz) | O(log nnz) | O(1) |
| `items()` iteration | O(nnz) | O(nnz) | O(n²) |
| `multiply(other)` | O(nnz^2) | O(nnz²/n) | O(n³) |

*nnz = number of non-zero entries, n = matrix dimension side length*

Explain your reasoning for each `?` in a sentence or two.
set(r, c, v):
O(nnz) because of the singular for loop and that it needs to check if it already exsists or not before setting

get(r, c):
O(nnz) because of the singular for loop and that it scans all stores entries before getting

items():
O(nnz) because of the singular for loop and that it loops over all non-zero entries

multiply(other):
O(nnz^2) because of nested loops over the non-zero entries

---

## Benchmark Results

Run `sparse_matrix_complexity.py` and paste the output here:

```
Time comparison of building the matrix ... set()
n=100: Sparse=0.001213s | CSR=0.000816s | NumPy=0.000134s
Time comparison of building the matrix ... set()
n=500: Sparse=0.026725s | CSR=0.000935s | NumPy=0.001773s
Time comparison of building the matrix ... set()
n=1000: Sparse=0.090951s | CSR=0.001062s | NumPy=0.002344s
Time comparison of random get() accesses
n=100: Sparse=0.000805s | CSR=0.002753s | NumPy=0.000053s
Time comparison of random get() accesses
n=500: Sparse=0.021981s | CSR=0.013479s | NumPy=0.000297s
Time comparison of random get() accesses
n=1000: Sparse=0.081351s | CSR=0.024581s | NumPy=0.000533s
Time comparison of items() full iteration
n=100: Sparse=0.000040s | CSR=0.000183s | NumPy=0.004408s
Time comparison of items() full iteration
n=500: Sparse=0.000175s | CSR=0.000255s | NumPy=0.115862s
Time comparison of items() full iteration
n=1000: Sparse=0.000341s | CSR=0.000281s | NumPy=0.458124s
Time comparison of multiply()
n=100: Sparse=0.003332s | CSR=0.000295s | NumPy=0.000653s
Time comparison of multiply()
n=500: Sparse=0.090176s | CSR=0.000328s | NumPy=0.006555s
Time comparison of multiply()
n=1000: Sparse=0.339125s | CSR=0.000353s | NumPy=0.064652s
```

---

## Space Complexity

| Representation | Space Used |
|----------------|-----------|
| Dense n×n      | O(n²)     |
| Your sparse    | O(nnz)      |

At what density (percentage of non-zero entries) does your sparse matrix
use *more* memory than a dense matrix?  Show your reasoning.
My sparse matrix would use more memory than a dense matrix when nnz = n² as htis would mean more overhead per entry
---

## Observations

1. How does your implementation compare to scipy in terms of speed?
-- My implementation compares to scipy in terms of speed as it's much slower than CSR.

2. When is a sparse representation faster than a dense one?
-- A sparse representation faster than a dense one over smaller iteration in items()

3. Was the overhead per entry (your structure vs. numpy array) noticeable?
Yes it was noticable with how the time of my sparse implementation significantly got slower with more iterations.

---

## Conclusions

I learned that sparse matricies are more useful when most values are zero but when most aren't and theyre a lot, other data structures would be better for shorter times. 

---

## References

List any resources (textbooks, websites, papers) you used.
