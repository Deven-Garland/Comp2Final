"""
test_bloom_filter.py - Basic tests for BloomFilter
"""
# Author: Deven Garland
# Date: 4/17/2026
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datastructures.bloom_filter import BloomFilter

def test_bloom_filter():
    bf = BloomFilter(bit_array_size=256, num_hashes=3)

    # Test 1: item we added should always return True
    bf.add("deven")
    assert bf.contains("deven") == True
    print("Test 1 passed: added item found")

    # Test 2: item we never added should return False
    assert bf.contains("notauser") == False
    print("Test 2 passed: missing item not found")

    # Test 3: len should match number of adds
    bf.add("ellie")
    bf.add("kimberly")
    assert len(bf) == 3
    print("Test 3 passed: len is correct")

    # Test 4: 'in' operator works
    assert "deven" in bf
    print("Test 4 passed: 'in' operator works")

    # Test 5: clear resets everything
    bf.clear()
    assert len(bf) == 0
    assert bf.contains("deven") == False
    print("Test 5 passed: clear works")

    # Test 6: no false negatives — anything we add must always be found
    usernames = ["alice", "bob", "charlie", "diana", "eve"]
    for name in usernames:
        bf.add(name)
    for name in usernames:
        assert bf.contains(name) == True
    print("Test 6 passed: no false negatives")

    print(f"\n{bf}")
    print("All tests passed!")

test_bloom_filter()