"""
test_hash_table.py - Tests for the HashTable implementation

Run this file directly to test the hash table:
    python tests/test_hash_table.py

Tests cover:
- Basic insert, get, remove
- Updating existing keys
- Bracket notation and the "in" operator
- KeyError on missing keys
- Collision handling (many keys in the same bucket)
- Automatic resizing when load factor gets high
- Large scale stress test with 10,000+ entries

Author: [Deven Garland]
Date: [4/17/2026]
Lab: Final Project - Hash Table
"""

import os
import sys
import random
import string
import time

# Add the project root to the path so we can import from datastructures/
# tests/ is inside datastructures/, so we need to go up two levels
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datastructures.hash_table import HashTable


# Keep track of how many tests passed and failed
passed = 0
failed = 0


def check(condition, test_name):
    """
    Helper that prints PASS or FAIL for a test and tracks the totals.
    """
    global passed, failed
    if condition:
        print(f"  PASS: {test_name}")
        passed += 1
    else:
        print(f"  FAIL: {test_name}")
        failed += 1


def test_basic_operations():
    """Test basic put, get, and len."""
    print("\nTest 1: Basic put, get, and len")
    t = HashTable()

    # Empty table
    check(len(t) == 0, "new table has size 0")
    check(t.get("nothing") is None, "get on empty table returns None")

    # Put a few values
    t.put("ellie", 100)
    t.put("bob", 200)
    t.put("carol", 300)

    check(len(t) == 3, "size is 3 after 3 inserts")
    check(t.get("ellie") == 100, "ellie maps to 100")
    check(t.get("bob") == 200, "bob maps to 200")
    check(t.get("carol") == 300, "carol maps to 300")
    check(t.get("nobody") is None, "missing key returns None")


def test_update_existing_key():
    """Test that updating a key does not grow the table."""
    print("\nTest 2: Updating existing keys")
    t = HashTable()

    t.put("ellie", 100)
    t.put("ellie", 999)   # update, not a new insert

    check(len(t) == 1, "size stays at 1 after update")
    check(t.get("ellie") == 999, "value was updated")


def test_remove():
    """Test removing keys from the table."""
    print("\nTest 3: Remove")
    t = HashTable()
    t.put("ellie", 100)
    t.put("bob", 200)

    # Remove an existing key
    result = t.remove("ellie")
    check(result is True, "remove returns True for existing key")
    check(len(t) == 1, "size drops to 1 after remove")
    check(t.get("ellie") is None, "ellie is no longer in table")
    check(t.get("bob") == 200, "bob is still in table")

    # Remove a key that was never there
    result = t.remove("nobody")
    check(result is False, "remove returns False for missing key")

    # Remove the same key twice
    result = t.remove("ellie")
    check(result is False, "remove returns False on second remove")


def test_bracket_notation():
    """Test __getitem__, __setitem__, and __delitem__."""
    print("\nTest 4: Bracket notation and dunders")
    t = HashTable()

    # Set with brackets
    t["ellie"] = 100
    t["bob"] = 200

    # Get with brackets
    check(t["ellie"] == 100, "bracket get works")
    check(t["bob"] == 200, "bracket get works for second key")

    # "in" operator
    check("ellie" in t, "in operator returns True for existing key")
    check("nobody" not in t, "in operator returns False for missing key")

    # del keyword
    del t["ellie"]
    check("ellie" not in t, "del removes key")
    check(len(t) == 1, "size drops after del")


def test_key_errors():
    """Test that missing keys raise KeyError with bracket access."""
    print("\nTest 5: KeyError on missing keys")
    t = HashTable()
    t["ellie"] = 100

    # Getting a missing key should raise KeyError
    raised = False
    try:
        _ = t["nobody"]
    except KeyError:
        raised = True
    check(raised, "accessing missing key raises KeyError")

    # Deleting a missing key should also raise KeyError
    raised = False
    try:
        del t["nobody"]
    except KeyError:
        raised = True
    check(raised, "del on missing key raises KeyError")


def test_contains():
    """Test the contains method and in operator."""
    print("\nTest 6: Contains method")
    t = HashTable()
    t.put("ellie", 100)

    check(t.contains("ellie") is True, "contains returns True for existing key")
    check(t.contains("nobody") is False, "contains returns False for missing key")


def test_iteration():
    """Test that iteration yields all keys."""
    print("\nTest 7: Iteration")
    t = HashTable()
    names = ["ellie", "bob", "carol", "dave", "eve"]
    for n in names:
        t[n] = n.upper()

    # Collect all keys from iteration
    collected = []
    for key in t:
        collected.append(key)

    check(len(collected) == len(names), "iteration yields all keys")
    # Order is not guaranteed in a hash table so sort before comparing
    check(sorted(collected) == sorted(names), "all expected keys are in iteration")


def test_collision_handling():
    """
    Test that the table handles collisions correctly by forcing many keys
    into a small table.
    """
    print("\nTest 8: Collision handling")
    # Start with a tiny table to force collisions
    t = HashTable(initial_capacity=4)
    # But turn off resize so we can see collisions by setting load factor high
    t.load_factor = 100.0

    # Put more keys than buckets, many will have to share buckets
    keys = [f"user{i}" for i in range(20)]
    for i, k in enumerate(keys):
        t.put(k, i)

    check(len(t) == 20, "all 20 keys stored despite collisions")

    # Verify every single key can still be looked up correctly
    all_found = True
    for i, k in enumerate(keys):
        if t.get(k) != i:
            all_found = False
            break
    check(all_found, "all 20 keys lookup correctly with collisions")


def test_automatic_resizing():
    """Test that the table grows when load factor is exceeded."""
    print("\nTest 9: Automatic resizing")
    t = HashTable(initial_capacity=4)
    starting_capacity = t.table_capacity

    # Insert enough keys to force at least one resize
    for i in range(20):
        t.put(f"key{i}", i)

    check(t.table_capacity > starting_capacity, "capacity grew after many inserts")
    check(len(t) == 20, "all entries preserved across resize")

    # Every key should still be findable after the resize
    all_ok = True
    for i in range(20):
        if t.get(f"key{i}") != i:
            all_ok = False
            break
    check(all_ok, "all keys still lookup correctly after resize")


def test_different_value_types():
    """Test that values can be any type not just numbers."""
    print("\nTest 10: Different value types")
    t = HashTable()

    # Simulate what we will actually store, player account dicts
    t.put("ellie", {"password_hash": "abc123", "wins": 5, "level": 10})
    t.put("bob", [1, 2, 3])
    t.put("carol", "just a string")
    t.put("dave", None)

    check(t.get("ellie")["wins"] == 5, "dict values work")
    check(t.get("bob") == [1, 2, 3], "list values work")
    check(t.get("carol") == "just a string", "string values work")
    check("dave" in t, "None as a value still counts as present")


def test_large_scale():
    """Stress test with 10,000+ entries to match the project requirements."""
    print("\nTest 11: Large scale (10,000 entries)")

    # Seeded random so results are repeatable
    random.seed(42)
    t = HashTable()

    # Generate 10,000 unique usernames
    names = set()
    while len(names) < 10000:
        length = random.randint(5, 12)
        name = "".join(random.choices(string.ascii_lowercase, k=length))
        names.add(name)
    names = list(names)

    # Time the inserts
    start = time.time()
    for n in names:
        t.put(n, n.upper())
    insert_time = time.time() - start

    check(len(t) == 10000, "all 10,000 entries stored")
    print(f"    Insert time: {insert_time:.3f} seconds for 10,000 entries")
    print(f"    Final capacity: {t.table_capacity}")
    print(f"    Load factor: {len(t) / t.table_capacity:.3f}")

    # Time the lookups
    start = time.time()
    all_ok = True
    for n in names:
        if t.get(n) != n.upper():
            all_ok = False
            break
    lookup_time = time.time() - start

    check(all_ok, "all 10,000 lookups return correct values")
    print(f"    Lookup time: {lookup_time:.3f} seconds for 10,000 lookups")
    print(f"    Average per lookup: {lookup_time / 10000 * 1_000_000:.2f} microseconds")


def run_all_tests():
    """Run every test function and print a summary."""
    print("=" * 60)
    print("HASH TABLE TEST SUITE")
    print("=" * 60)

    test_basic_operations()
    test_update_existing_key()
    test_remove()
    test_bracket_notation()
    test_key_errors()
    test_contains()
    test_iteration()
    test_collision_handling()
    test_automatic_resizing()
    test_different_value_types()
    test_large_scale()

    # Final summary
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("All tests passed.")
    else:
        print(f"{failed} test(s) failed.")


if __name__ == "__main__":
    run_all_tests()