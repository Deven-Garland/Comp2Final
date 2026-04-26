"""
sparse_matrix_tests.py - Tests for SparseMatrix

Write tests for ALL methods of your SparseMatrix implementation.
You may use AI to help generate edge cases, but make sure you understand
every test before submitting.

Run with:
    cd code/game/datastructures/tests
    python sparse_matrix_tests.py

Author: [Deven Garland]
Date:   [4/11/2026]
Lab:    Lab 6 - Sparse World Map
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datastructures.sparse_matrix import SparseMatrix
#from scipy.sparse import csr_matrix


# ==========================================================================
def test_set_and_get():
    # Create a matrix
    m = SparseMatrix(default=0)
    
    # Set a value at position (1,2)
    m.set(1, 2, 5)
    
    # Check that we get the same value back
    assert m.get(1, 2) == 5


def test_default_value():
    # Create a matrix with default 0
    m = SparseMatrix(default=0)
    
    # Check a position that was never set
    # It should return the default
    assert m.get(10, 10) == 0


def test_custom_default():
    # Create a matrix with default -1
    m = SparseMatrix(default=-1)
    
    # Check a position that was never set
    assert m.get(0, 0) == -1


def test_len_empty():
    # Create an empty matrix
    m = SparseMatrix()
    
    # Length should be 0 since nothing is stored
    assert len(m) == 0


def test_len_after_set():
    # Create a matrix
    m = SparseMatrix()
    
    # Add two values
    m.set(0, 0, 5)
    m.set(1, 1, 10)
    
    # Length should be 2
    assert len(m) == 2


def test_items():
    # Create a matrix
    m = SparseMatrix()
    
    # Add values
    m.set(0, 1, 3)
    m.set(2, 2, 7)

    # Convert items to a list so we can check it
    items = list(m.items())
    
    # Check that both values exist
    assert ((0, 1), 3) in items
    assert ((2, 2), 7) in items
    
    # Make sure there are only 2 items
    assert len(items) == 2


def test_overwrite():
    # Create a matrix
    m = SparseMatrix()
    
    # Set a value
    m.set(0, 0, 5)
    
    # Set the same position again
    m.set(0, 0, 10)
    
    # Value should be updated
    assert m.get(0, 0) == 10
    
    # Still only one entry stored
    assert len(m) == 1


def test_set_to_default_removes_entry():
    # Create a matrix
    m = SparseMatrix()
    
    # Add a value
    m.set(0, 0, 5)
    
    # Set it back to default (0)
    m.set(0, 0, 0)
    
    # Should now return default
    assert m.get(0, 0) == 0
    
    # Entry should be removed
    assert len(m) == 0


def test_large_sparse():
    # Create a matrix
    m = SparseMatrix()

    # Add only 10 values
    for i in range(1,11):
        m.set(i, i, i)

    # Even though matrix is "large", only 10 entries exist
    assert len(m) == 10


def test_items_consistent_with_get():
    # Create a matrix
    m = SparseMatrix()
    
    # Add values
    m.set(1, 2, 5)
    m.set(3, 4, 8)

    # Loop through all stored items
    for (r, c), v in m.items():
        
        # Each value should match what get() returns
        assert m.get(r, c) == v


def test_multiply_identity():
    # Create matrix A
    A = SparseMatrix()
    A.set(0, 0, 2)
    A.set(1, 1, 3)

    # Create identity matrix I
    I = SparseMatrix()
    I.set(0, 0, 1)
    I.set(1, 1, 1)

    # Multiply A * I
    result = A.multiply(I)

    # Result should be same as A
    assert result.get(0, 0) == 2
    assert result.get(1, 1) == 3


def test_multiply_basic():
    # Create matrix A
    A = SparseMatrix()
    A.set(0, 0, 1)
    A.set(0, 1, 2)

    # Create matrix B
    B = SparseMatrix()
    B.set(0, 0, 3)
    B.set(1, 0, 4)

    # Multiply A * B
    result = A.multiply(B)

    # Expected result: (1*3 + 2*4) = 11
    assert result.get(0, 0) == 11


def test_multiply_zero():
    # Create matrix A
    A = SparseMatrix()
    A.set(0, 0, 5)

    # Create empty matrix (all zeros)
    Z = SparseMatrix()

    # Multiply A * Z
    result = A.multiply(Z)

    # Result should have no stored values
    assert len(result) == 0


def test_str():
    # Create matrix
    m = SparseMatrix()
    
    # Add a value
    m.set(0, 0, 5)

    # Convert to string
    s = str(m)
    
    # Check that it is a string
    assert isinstance(s, str)
    
    # Check that it is not empty
    assert len(s) > 0



# ==========================================================================


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
    print("All tests passed!")
