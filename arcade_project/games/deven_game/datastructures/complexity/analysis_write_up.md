# Sparse Matrix Complexity Analysis

**Name:** [Deven Garland]
**Date:** [4/11/2026]
**Implementation:** COO

---

## Overview
I choose to use the COO due to the simplixity of adding it to my game by using our already built array class. 
This approach works well for the tile-map use case because most of the values in the matrix are the same (default), 
so storing only the non-default values saves memory. Some trade-offs of making the sparse matrix this way are that
the get and set method are slower since they have to scanthrough all stroed entries instead of directing indexing like
a dense matrix or hasing like DOK. 


---

## Time Complexity

Fill in the `?` cells after analysing your implementation.

| Operation | Your SparseMatrix | scipy sparse (CSR) | numpy dense |
|-----------|-------------------|--------------------|-------------|
| `set(r, c, v)` | O(nnz)         | O(nnz) amortised   | O(1)   |
| `get(r, c)` | O(nnz)            | O(log nnz)         | O(1)  |
| `items()` iteration | O(nnz)    | O(nnz)             | O(n²)     |
| `multiply(other)` | O(nnz^2)    | O(nnz²/n)          | O(n³)  |

*nnz = number of non-zero entries, n = matrix dimension side length*

Explain your reasoning for each `?` in a sentence or two.
set: We have to loop through all of the entries to check if the row and col exisit before inserting
get: We have to loop through all of the entries until there is a match
items: We will yield every entry so we have to pass through the entire list
multiply: We have to loop through both matrices in order to multiply them together. 
---

## Benchmark Results

Run `sparse_matrix_complexity.py` and paste the output here:

```
=== Summary Table ===
Operation               SparseMatrix           scipy           numpy
-----------------------------------------------------------------
build                        0.6443s         0.0019s         0.0041s
get                          0.2648s         0.0279s         0.0016s
items                        0.0042s         0.0011s         0.0593s
multiply                     0.0013s         0.0007s         0.0001s

=== Memory Usage ===
SparseMatrix  memory:   current=51.11KB  peak=51.23KB
scipy         memory:   current=32.32KB  peak=72.43KB
numpy         memory:   current=1953.22KB  peak=1953.36KB
```

---

## Space Complexity

| Representation | Space Used |
|----------------|-----------|
| Dense n×n      | O(n²)     |
| Your sparse    | O(nnz)      |

At what density (percentage of non-zero entries) does your sparse matrix
use *more* memory than a dense matrix?  Show your reasoning.

We saw that our SparseMatrix used 1% density of the 500X500 matrix and resulted in 51.11 KB being used. We know that numpy stored the full 500x500 matrix and used 1953.22 kb. If 51.11 kb was equal to 1% if we made it 10% that would be 510 kb and if we made it 40% it would give us 2040 KB (510*4). This means that at 40% density our sparse matrix uses more memory than the a dense matrix. 
---

## Observations

1. How does your implementation compare to scipy in terms of speed?
our impliementation is slower than scipy in every one of the tested methods. This is because we are just using arrays to store our data for the sparse matrix which means we need to make multiple loops to build, get, yield, and multiply. 
2. When is a sparse representation faster than a dense one?
Whenever there are many default values (0's) and a small number of values. So when we are working with a large matrix that only has a small number of values that are actually stored and not 0's
3. Was the overhead per entry (your structure vs. numpy array) noticeable?
Yes, the numpy matrix has to hold the full 500x500 which gives us a very large memory ussage. For the sparse matrix we only have to hold the non zero numbers which is 1% of the 500x500 which is 2500.

---

## Conclusions
From this experiment, I learned that sparse data structures are very useful for storing large datasets that contain mostly default/0's. They save a significant amount of memory compared to dense matrices like NumPy when the data is sparse. However, I also learned that simple implementations can be slower for operations like searching and updating compared to optimized libraries like SciPy.

---

## References

List any resources (textbooks, websites, papers) you used.
https://www.geeksforgeeks.org/dsa/sparse-matrix-representation/
Claude: Linked in ai_conversations