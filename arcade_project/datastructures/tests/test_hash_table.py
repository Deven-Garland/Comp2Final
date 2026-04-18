"""
test_hash_table.py - Tests for the HashTable implementation

Run from the project root:
    python datastructures/tests/test_hash_table.py

Author: Ellie Lutz
Date: [4/17/2026]
Lab: Final Project - Hash Table
"""

import os
import sys
import time

# Add the project root to the path so we can import from datastructures/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datastructures.hash_table import HashTable


# Track totals
passed = 0
failed = 0


def check(condition, test_name):
    """Print PASS or FAIL for a test."""
    global passed, failed
    if condition:
        print(f"  PASS: {test_name}")
        passed += 1
    else:
        print(f"  FAIL: {test_name}")
        failed += 1


def test_basics():
    """Put, get, len, and missing keys."""
    print("\nTest 1: Basic operations")
    t = HashTable()
    check(len(t) == 0, "new table has size 0")

    t.put("ellie", 100)
    t.put("bob", 200)
    check(len(t) == 2, "size is 2 after 2 inserts")
    check(t.get("ellie") == 100, "get returns the right value")
    check(t.get("nobody") is None, "missing key returns None")


def test_update():
    """Updating a key should not grow size."""
    print("\nTest 2: Update existing key")
    t = HashTable()
    t.put("ellie", 100)
    t.put("ellie", 999)
    check(len(t) == 1, "size stays at 1 after update")
    check(t.get("ellie") == 999, "value was updated")


def test_remove():
    """Removing keys."""
    print("\nTest 3: Remove")
    t = HashTable()
    t.put("ellie", 100)

    check(t.remove("ellie") is True, "remove returns True for existing key")
    check(t.get("ellie") is None, "key is gone after remove")
    check(t.remove("ellie") is False, "remove returns False for missing key")


def test_brackets():
    """Bracket notation, in operator, and del."""
    print("\nTest 4: Brackets and in")
    t = HashTable()
    t["ellie"] = 100

    check(t["ellie"] == 100, "bracket get works")
    check("ellie" in t, "in operator works")
    check("nobody" not in t, "in operator returns False for missing key")

    del t["ellie"]
    check("ellie" not in t, "del removes key")

    # Missing key should raise KeyError
    raised = False
    try:
        _ = t["nobody"]
    except KeyError:
        raised = True
    check(raised, "missing key raises KeyError")


def test_resizing_and_collisions():
    """Stress test with enough inserts to force collisions and resizes."""
    print("\nTest 5: Collisions and resizing")
    t = HashTable(initial_capacity=4)
    starting_capacity = t.table_capacity

    # Insert way more than initial capacity to force collisions and resizing
    for i in range(100):
        t.put(f"user{i}", i)

    check(len(t) == 100, "all 100 entries stored")
    check(t.table_capacity > starting_capacity, "capacity grew after many inserts")

    # Every key should still be findable
    all_ok = all(t.get(f"user{i}") == i for i in range(100))
    check(all_ok, "all keys lookup correctly after collisions and resize")


def test_large_scale():
    """Quick performance check with 10,000 entries to match project requirements."""
    print("\nTest 6: Large scale (10,000 entries)")
    t = HashTable()

    start = time.time()
    for i in range(10000):
        t.put(f"player{i}", i)
    insert_time = time.time() - start

    check(len(t) == 10000, "all 10,000 entries stored")
    check(t.get("player5000") == 5000, "lookup works at scale")
    print(f"    Insert time: {insert_time:.3f} seconds")
    print(f"    Final capacity: {t.table_capacity}, load factor: {len(t)/t.table_capacity:.3f}")


def run_all_tests():
    print("=" * 50)
    print("HASH TABLE TESTS")
    print("=" * 50)

    test_basics()
    test_update()
    test_remove()
    test_brackets()
    test_resizing_and_collisions()
    test_large_scale()

    print("\n" + "=" * 50)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()