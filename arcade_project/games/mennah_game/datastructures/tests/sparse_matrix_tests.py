"""
sparse_matrix_tests.py - Tests for SparseMatrix

Write tests for ALL methods of your SparseMatrix implementation.
You may use AI to help generate edge cases, but make sure you understand
every test before submitting.

Run with:
    cd code/game/datastructures/tests
    python sparse_matrix_tests.py

Author: Mennah Khaled Dewidar
Date:   4/12/2026
Lab:    Lab 6 - Sparse World Map
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datastructures.sparse_matrix import SparseMatrix
from scipy.sparse import csr_matrix


# ==========================================================================
# TODO: Write your tests below
#
# Suggested test ideas (each as a separate function):
#
def test_set_and_get():
    matrix = SparseMatrix(default=0)
    matrix.set(1, 2, 5)
    assert matrix.get(1, 2) == 5
    assert matrix.get(0, 0) == 0

def test_default_value():
    matrix = SparseMatrix(default=-1)
    assert matrix.get(5, 5) == -1

def test_custom_default():
    matrix = SparseMatrix()
    assert len(matrix) == 0

def test_len_empty():
    matrix = SparseMatrix()
    assert len(matrix) == 0

def test_len_after_set():
    matrix = SparseMatrix()
    matrix.set(1, 1, 10)
    matrix.set(2, 2, 20)
    assert len(matrix) == 2

def test_items():
    """items() should yield exactly the non-default entries."""
    matrix = SparseMatrix()
    matrix.set(1, 1, 5)
    matrix.set(2, 2, 10)

    items = list(matrix.items())
    assert ((1, 1), 5) in items
    assert ((2, 2), 10) in items
    assert len(items) == 2

def test_overwrite():
    """Setting a position twice keeps only the latest value."""
    matrix = SparseMatrix()
    matrix.set(1, 1, 5)
    matrix.set(1, 1, 9)
    assert matrix.get(1, 1) == 9
    assert len(matrix) == 1

def test_set_to_default_removes_entry():
    """set(r, c, default) should remove the entry so len() decreases."""
    matrix = SparseMatrix(default=0)
    matrix.set(2, 3, 7)
    matrix.set(2, 3, 0)
    assert matrix.get(2, 3) == 0
    assert len(matrix) == 0

def test_large_sparse():
    """A 1000x1000 matrix with 10 entries should use minimal memory."""
    matrix = SparseMatrix(default=0)

    for i in range(10):
        matrix.set(i, i, i + 1)

    assert len(matrix) == 10
    for i in range(10):
        assert matrix.get(i, i) == i + 1

def test_items_consistent_with_get():
    """Every (r, c) yielded by items() should match get(r, c)."""
    matrix = SparseMatrix(default=0)
    matrix.set(3, 4, 8)

    for (r, c), v in matrix.items():
        assert matrix.get(r, c) == v

def test_multiply_identity():
    """A * I == A  for a 2x2 identity matrix."""
    a = SparseMatrix(default=0)
    I = SparseMatrix(default=0)

    # a = [[1,2],[3,4]]
    a.set(0, 0, 1)
    a.set(0, 1, 2)
    a.set(1, 0, 3)
    a.set(1, 1, 4)

    # identity matrix
    I.set(0, 0, 1)
    I.set(1, 1, 1)

    result = a.multiply(I)

    assert result.get(0, 0) == 1
    assert result.get(0, 1) == 2
    assert result.get(1, 0) == 3
    assert result.get(1, 1) == 4

def test_multiply_basic():
    """Hand-computed 2x2 example."""
    a = SparseMatrix(default=0)
    b = SparseMatrix(default=0)

    # a = [[1,2],[3,4]]
    a.set(0, 0, 1)
    a.set(0, 1, 2)
    a.set(1, 0, 3)
    a.set(1, 1, 4)

    # b = [[5,6],[7,8]]
    b.set(0, 0, 5)
    b.set(0, 1, 6)
    b.set(1, 0, 7)
    b.set(1, 1, 8)

    result = a.multiply(b)

    assert result.get(0, 0) == 19   # 1*5 + 2*7
    assert result.get(0, 1) == 22   # 1*6 + 2*8
    assert result.get(1, 0) == 43   # 3*5 + 4*7
    assert result.get(1, 1) == 50   # 3*6 + 4*8
    
def test_multiply_zero():
    """A * Z == all-zeros (empty sparse matrix)."""
    a = SparseMatrix(default=0)
    z = SparseMatrix(default=0)

    a.set(0, 0, 5)
    a.set(1, 1, 7)

    result = a.multiply(z)

    assert len(result) == 0 

def test_str():
    """__str__ should return a non-empty string."""
    matrix = SparseMatrix()
    matrix.set(1, 2, 5)
    s = str(matrix)
    assert isinstance(s, str)
    assert "SparseMatrix" in s

# ==========================================================================


if __name__ == '__main__':
    # TODO: call your tests here
    test_set_and_get()
    test_default_value()
    test_len_empty()
    test_len_after_set()
    test_overwrite()
    test_set_to_default_removes_entry()
    test_items()
    test_items_consistent_with_get()
    test_large_sparse()
    test_multiply_identity()
    test_multiply_zero()
    test_multiply_basic()
    test_str()
    print("All tests passed!")
