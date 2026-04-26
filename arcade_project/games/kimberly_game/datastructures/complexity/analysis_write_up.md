# Linked List Complexity Analysis Write-Up

**Author:** [Kimberly Olea]
**Date:** [4/3/26]
**Lab:** Lab 5 - NPC Patrol Paths with Linked Lists

---

## Overview

[Brief description of what you analyzed and which operations you tested.]
I analyzed the performance of my linked list patrol path implementation. I tested add_waypoint() operation that adds a new waypoint node to the patrol path. The get_next_waypoint() that returns the next waypoint for NPC movement.
---

## Time Complexity Analysis

### Operation Tested: `add_waypoint()`

**Theoretical Complexity:** O(1)

**Results:**

| n (waypoints) | Time (seconds) |
|--------------|----------------|
| 100          |  ~ 0s          |
| 1,000        |  ~ 0.002s      |
| 10,000       |  ~ 0.01s       |
| 100,000      |  ~0.25s        |

**Theory vs. Practice:**
[Does your measured time match the theoretical prediction? When you double n, what happens to the time? Report actual ratios.]
add_waypoint is O(1) because the linked list keeps a tail pointer, so each new waypoint can be added directly to the end without traversing the list. Each waypoint shows increased time which shows roughly linear growth and is expected whne repeating a constant time operation n times.

**Discrepancies:**
[If measurements don't perfectly match theory, why? Consider Python overhead, caching, small input sizes, etc.]
The timings are not perfect because of python overhead and small timing inaccuracies for low input sizes that affect measurements.
---

### Operation Tested: `get_next_waypoint()`

**Theoretical Complexity:** O(1)

**Results:**

| n (waypoints) | Time (seconds) |
|--------------|----------------|
| 100          | very small      |
| 1,000        | vert small      |
| 10,000       |   small         |
| 100,000      |  larger         |

**Theory vs. Practice:**
[Does your measured time match the theoretical prediction?]
It only returns the current waypoint and updates a pointer to the next or previous node makinng the complexity O(1).

**Discrepancies:**
[Explain any differences from theoretical expectations.]
Small differences in constant time behavior are from python overhead, and timing noise.

---

## Space Complexity Analysis

**Theoretical Complexity:** O(n)

**Results:**

| n (waypoints) | Memory (bytes) |
|--------------|----------------|
| 100          | grows lineaerly|
| 500          |large           |
| 1,000        |about double    |
| 5,000        |much larger     |

**Theory vs. Practice:**
[Does memory usage grow as expected? What is the per-node overhead?]
Space complexity is O(n) since each waypoint is stores as a seperate node. Number of waypoints increases and memory usage should increase about linearly. Each node also has extra python overhead.

---

## Linked Lists vs. Arrays

[Compare the linked list operations you implemented against the ArrayList from Lab 3. When is a linked list better? When is an array better? Use specific numbers from your experiments.]
My ArrayList was faster than the linked list for this insertion in this implementation. A linked list is better when the data needs to be connected node by node such as npc control paths. An array is better whne lower memory overheard and faster practical perfomance are more important.

---

## Conclusions

[What did you learn about your implementation? Include specific numbers (e.g., "Adding 10,000 waypoints took X seconds, while 20,000 took Y seconds — a ratio of Z, confirming O(n) scaling"). What are the practical implications for NPC patrol paths in your game?]
I learned both operations are O(1) in my linked list implementation. The total runtime still increases as more operations are performed. Adding 10000 waypoints took 0.02 seconds while adding 100000 took about 0.25 seconds which is a large increase consistent with linear growth. Linked lists are a good fit for NPC control paths. Thye make one way, circular, and back and forth movement easy to model. 
