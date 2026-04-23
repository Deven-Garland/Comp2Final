"""
sparse_matrix_tests.py - Tests for SparseMatrix

Write tests for ALL methods of your SparseMatrix implementation.
You may use AI to help generate edge cases, but make sure you understand
every test before submitting.

Run with:
    cd code/game/datastructures/tests
    python sparse_matrix_tests.py

Author: Ellie Lutz
Date:   04/12/2026
Lab:    Lab 6 - Sparse World Map
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datastructures.sparse_matrix import SparseMatrix


# Store a value and make sure we can retrieve it
def test_set_and_get():
    m = SparseMatrix(default=0)
    m.set(0, 0, 5)
    assert m.get(0, 0) == 5

# A position we never set should return the default value
def test_default_value():
    m = SparseMatrix(default=0)
    assert m.get(9, 9) == 0

# Same as above but with -1 as the default (like a tile map)
def test_custom_default():
    m = SparseMatrix(default=-1)
    assert m.get(0, 0) == -1

# A brand new matrix should have 0 entries
def test_len_empty():
    m = SparseMatrix(default=0)
    assert len(m) == 0

# After setting 2 values, length should be 2
def test_len_after_set():
    m = SparseMatrix(default=0)
    m.set(0, 0, 1)
    m.set(1, 1, 2)
    assert len(m) == 2

# items() should return exactly the non-default entries we set
def test_items():
    m = SparseMatrix(default=0)
    m.set(0, 0, 1)
    m.set(1, 2, 3)
    items = list(m.items())
    assert len(items) == 2
    coords = [coord for coord, val in items]
    assert (0, 0) in coords
    assert (1, 2) in coords

# Setting the same position twice should keep the newest value
def test_overwrite():
    m = SparseMatrix(default=0)
    m.set(0, 0, 5)
    m.set(0, 0, 99)
    assert m.get(0, 0) == 99
    assert len(m) == 1

# Setting a position to the default value should delete it from storage
def test_set_to_default_removes_entry():
    m = SparseMatrix(default=0)
    m.set(0, 0, 5)
    m.set(0, 0, 0)
    assert len(m) == 0
    assert m.get(0, 0) == 0

# A huge matrix with only 10 entries should still only store 10 entries
def test_large_sparse():
    m = SparseMatrix(rows=1000, cols=1000, default=0)
    for i in range(10):
        m.set(i, i, i + 1)
    assert len(m) == 10

# Every entry returned by items() should match what get() returns
def test_items_consistent_with_get():
    m = SparseMatrix(default=0)
    m.set(2, 3, 7)
    m.set(5, 1, 4)
    for (r, c), v in m.items():
        assert m.get(r, c) == v

# Multiplying any matrix by the identity matrix should give back the same matrix
def test_multiply_identity():
    a = SparseMatrix(rows=2, cols=2, default=0)
    a.set(0, 0, 1); a.set(0, 1, 2)
    a.set(1, 0, 3); a.set(1, 1, 4)

    identity = SparseMatrix(rows=2, cols=2, default=0)
    identity.set(0, 0, 1)
    identity.set(1, 1, 1)

    result = a.multiply(identity)
    assert result.get(0, 0) == 1
    assert result.get(0, 1) == 2
    assert result.get(1, 0) == 3
    assert result.get(1, 1) == 4

# Hand-computed: [[1,2],[3,4]] * [[5,6],[7,8]] = [[19,22],[43,50]]
def test_multiply_basic():
    a = SparseMatrix(rows=2, cols=2, default=0)
    a.set(0, 0, 1); a.set(0, 1, 2)
    a.set(1, 0, 3); a.set(1, 1, 4)

    b = SparseMatrix(rows=2, cols=2, default=0)
    b.set(0, 0, 5); b.set(0, 1, 6)
    b.set(1, 0, 7); b.set(1, 1, 8)

    result = a.multiply(b)
    assert result.get(0, 0) == 19
    assert result.get(0, 1) == 22
    assert result.get(1, 0) == 43
    assert result.get(1, 1) == 50

# Multiplying by an all-zero matrix should give all zeros
def test_multiply_zero():
    a = SparseMatrix(rows=2, cols=2, default=0)
    a.set(0, 0, 5)
    a.set(1, 1, 3)

    zero = SparseMatrix(rows=2, cols=2, default=0)

    result = a.multiply(zero)
    assert result.get(0, 0) == 0
    assert result.get(1, 1) == 0
    assert len(result) == 0

# __str__ should return a non-empty string when there are entries
def test_str():
    m = SparseMatrix(default=0)
    m.set(0, 0, 1)
    assert len(str(m)) > 0

# __str__ on an empty matrix should mention "empty"
def test_str_empty():
    m = SparseMatrix(default=0)
    assert "empty" in str(m).lower()


if __name__ == '__main__':
    test_set_and_get()
    test_default_value()
    test_custom_default()
    test_len_empty()
    test_len_after_set()
    test_items()
    test_overwrite()
    test_set_to_default_removes_entry()
    test_large_sparse()
    test_items_consistent_with_get()
    test_multiply_identity()
    test_multiply_basic()
    test_multiply_zero()
    test_str()
    test_str_empty()
    print("All tests passed!")