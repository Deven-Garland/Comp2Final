# code/datastructures/tests/heap_tests.py
import sys
sys.path.append('..')  # Add parent directory to path
from heap import MinHeap, MaxHeap
 
 
def test_minheap_creation():
    """Test creating a MinHeap"""
    print("Testing MinHeap creation...")
 
    min_heap = MinHeap()
    assert min_heap.size == 0
    assert min_heap.capacity == 10
 
    mn2 = MinHeap(20)
    assert mn2.capacity == 20
 
    print("✓ MinHeap creation works!")
 
 
def test_maxheap_creation():
    """Test creating a MaxHeap"""
    print("Testing MaxHeap creation...")
 
    max_heap = MaxHeap()
    assert max_heap.size == 0
    assert max_heap.capacity == 10
 
    mx2 = MaxHeap(20)
    assert mx2.capacity == 20
 
    print("✓ MaxHeap creation works!")
 
 
def test_minheap_insert():
    min_heap = MinHeap()
    min_heap.insert(30)
    min_heap.insert(10)
    min_heap.insert(20)
    assert min_heap.get_min() == 10
    assert min_heap.get_size() == 3
    print("✓ MinHeap insert works!")
 
 
def test_maxheap_insert():
    max_heap = MaxHeap()
    max_heap.insert(10)
    max_heap.insert(50)
    max_heap.insert(30)
    assert max_heap.get_max() == 50
    assert max_heap.get_size() == 3
    print("✓ MaxHeap insert works!")
 
 
def test_minheap_get_min():
    min_heap = MinHeap()
    assert min_heap.get_min() is None
    min_heap.insert(30)
    min_heap.insert(5)
    min_heap.insert(10)
    assert min_heap.get_min() == 5
    print("✓ MinHeap get_min works!")
 
 
def test_maxheap_get_max():
    max_heap = MaxHeap()
    assert max_heap.get_max() is None
    max_heap.insert(10)
    max_heap.insert(50)
    max_heap.insert(30)
    assert max_heap.get_max() == 50
    print("✓ MaxHeap get_max works!")
 
 
def test_minheap_remove_min():
    min_heap = MinHeap()
    assert min_heap.remove_min() is None
    min_heap.insert(30)
    min_heap.insert(5)
    min_heap.insert(10)
    assert min_heap.remove_min() == 5
    assert min_heap.get_min() == 10
    assert min_heap.get_size() == 2
    print("✓ MinHeap remove_min works!")
 
 
def test_maxheap_remove_max():
    max_heap = MaxHeap()
    assert max_heap.remove_max() is None
    max_heap.insert(10)
    max_heap.insert(50)
    max_heap.insert(30)
    assert max_heap.remove_max() == 50
    assert max_heap.get_max() == 30
    assert max_heap.get_size() == 2
    print("✓ MaxHeap remove_max works!")
 
 
def test_minheap_is_empty():
    min_heap = MinHeap()
    assert min_heap.is_empty() == True
    min_heap.insert(1)
    assert min_heap.is_empty() == False
    print("✓ MinHeap is_empty works!")
 
 
def test_maxheap_is_empty():
    max_heap = MaxHeap()
    assert max_heap.is_empty() == True
    max_heap.insert(1)
    assert max_heap.is_empty() == False
    print("✓ MaxHeap is_empty works!")
 
 
def test_minheap_get_size():
    min_heap = MinHeap()
    assert min_heap.get_size() == 0
    min_heap.insert(10)
    min_heap.insert(20)
    min_heap.insert(30)
    assert min_heap.get_size() == 3
    print("✓ MinHeap get_size works!")
 
 
def test_maxheap_get_size():
    max_heap = MaxHeap()
    assert max_heap.get_size() == 0
    max_heap.insert(10)
    max_heap.insert(20)
    max_heap.insert(30)
    assert max_heap.get_size() == 3
    print("✓ MaxHeap get_size works!")
 
 
def test_minheap_clear():
    min_heap = MinHeap()
    min_heap.insert(10)
    min_heap.insert(20)
    min_heap.clear()
    assert min_heap.size == 0
    assert min_heap.is_empty() == True
    print("✓ MinHeap clear works!")
 
 
def test_maxheap_clear():
    max_heap = MaxHeap()
    max_heap.insert(10)
    max_heap.insert(20)
    max_heap.clear()
    assert max_heap.size == 0
    assert max_heap.is_empty() == True
    print("✓ MaxHeap clear works!")
 
 
def test_minheap_str():
    min_heap = MinHeap()
    min_heap.insert(30)
    min_heap.insert(10)
    min_heap.insert(20)
    assert str(min_heap) == "[10, 30, 20]"
    print("✓ MinHeap __str__ works!")
 
 
def test_maxheap_str():
    max_heap = MaxHeap()
    max_heap.insert(10)
    max_heap.insert(50)
    max_heap.insert(30)
    assert str(max_heap) == "[50, 10, 30]"
    print("✓ MaxHeap __str__ works!")
 
 
def test_minheap_repr():
    min_heap = MinHeap()
    min_heap.insert(10)
    min_heap.insert(5)
    assert repr(min_heap) == "[5, 10]"
    print("✓ MinHeap __repr__ works!")
 
 
def test_maxheap_repr():
    max_heap = MaxHeap()
    max_heap.insert(10)
    max_heap.insert(50)
    assert repr(max_heap) == "[50, 10]"
    print("✓ MaxHeap __repr__ works!")
 
 
def test_minheap_iter():
    min_heap = MinHeap()
    min_heap.insert(30)
    min_heap.insert(5)
    min_heap.insert(10)
    result = []
    for item in min_heap:
        result.append(item)
    assert result[0] == 5
    assert result[1] == 30
    assert result[2] == 10
    print("✓ MinHeap __iter__ works!")
 
 
def test_maxheap_iter():
    max_heap = MaxHeap()
    max_heap.insert(10)
    max_heap.insert(50)
    max_heap.insert(30)
    result = []
    for item in max_heap:
        result.append(item)
    assert result[0] == 50
    assert result[1] == 10
    assert result[2] == 30
    print("✓ MaxHeap __iter__ works!")
 
 
# Edge cases:
def test_minheap_double():
    # the purpose of this edge case is to test that the heap grows correctly
    # when we insert more values than the initial capacity
    min_heap = MinHeap(3)
    min_heap.insert(10)
    min_heap.insert(20)
    min_heap.insert(30)
    assert min_heap.capacity == 3
    min_heap.insert(40)
    assert min_heap.capacity == 6
    assert min_heap.get_min() == 10
    assert min_heap.get_size() == 4
    print("✓ Edge cases for MinHeap double works!")
 
 
def test_maxheap_double():
    # the purpose of this edge case is to test that the heap grows correctly
    # when we insert more values than the initial capacity
    max_heap = MaxHeap(3)
    max_heap.insert(10)
    max_heap.insert(20)
    max_heap.insert(30)
    assert max_heap.capacity == 3
    max_heap.insert(40)
    assert max_heap.capacity == 6
    assert max_heap.get_max() == 40
    assert max_heap.get_size() == 4
    print("✓ Edge cases for MaxHeap double works!")
 
 
def test_minheap_remove_edge():
    # the purpose of this edge case is to test removing from an empty heap
    # and that the heap property is maintained after multiple removals
    min_heap = MinHeap()
    assert min_heap.remove_min() is None
    min_heap.insert(30)
    min_heap.insert(10)
    min_heap.insert(50)
    min_heap.insert(5)
    assert min_heap.remove_min() == 5
    assert min_heap.remove_min() == 10
    assert min_heap.remove_min() == 30
    assert min_heap.remove_min() == 50
    assert min_heap.remove_min() is None
    print("✓ Edge cases for MinHeap remove_min work!")
 
 
def test_maxheap_remove_edge():
    # the purpose of this edge case is to test removing from an empty heap
    # and that the heap property is maintained after multiple removals
    max_heap = MaxHeap()
    assert max_heap.remove_max() is None
    max_heap.insert(30)
    max_heap.insert(10)
    max_heap.insert(50)
    max_heap.insert(5)
    assert max_heap.remove_max() == 50
    assert max_heap.remove_max() == 30
    assert max_heap.remove_max() == 10
    assert max_heap.remove_max() == 5
    assert max_heap.remove_max() is None
    print("✓ Edge cases for MaxHeap remove_max work!")
 
 
def test_minheap_order():
    # the purpose of this edge case is to verify that no matter what order
    # values are inserted, the smallest always ends up at the top
    min_heap = MinHeap()
    min_heap.insert(100)
    min_heap.insert(1)
    min_heap.insert(50)
    min_heap.insert(2)
    min_heap.insert(75)
    assert min_heap.get_min() == 1
    print("✓ Edge cases for MinHeap order work!")
 
 
def test_maxheap_order():
    # the purpose of this edge case is to verify that no matter what order
    # values are inserted, the largest always ends up at the top
    max_heap = MaxHeap()
    max_heap.insert(1)
    max_heap.insert(100)
    max_heap.insert(50)
    max_heap.insert(2)
    max_heap.insert(75)
    assert max_heap.get_max() == 100
    print("✓ Edge cases for MaxHeap order work!")
 
 
def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("Running Binary Heap Tests")
    print("="*50)
 
    test_minheap_creation()
    test_maxheap_creation()
    test_minheap_insert()
    test_maxheap_insert()
    test_minheap_get_min()
    test_maxheap_get_max()
    test_minheap_remove_min()
    test_maxheap_remove_max()
    test_minheap_is_empty()
    test_maxheap_is_empty()
    test_minheap_get_size()
    test_maxheap_get_size()
    test_minheap_clear()
    test_maxheap_clear()
    test_minheap_str()
    test_maxheap_str()
    test_minheap_repr()
    test_maxheap_repr()
    test_minheap_iter()
    test_maxheap_iter()
 
    test_minheap_double()
    test_maxheap_double()
    test_minheap_remove_edge()
    test_maxheap_remove_edge()
    test_minheap_order()
    test_maxheap_order()
 
    print("="*50)
    print("✓ ALL TESTS PASSED!")
    print("="*50)
 
 
if __name__ == "__main__":
    run_all_tests()