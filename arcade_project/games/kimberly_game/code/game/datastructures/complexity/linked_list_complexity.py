"""
linked_list_complexity.py - Analyze time complexity of Linked List operations

Measures actual performance of Linked List operations and compares to theoretical Big O.

Author: [Your Name]
Date: [Date]
Lab: Lab 5 - NPC Patrol Paths with Linked Lists
"""

import sys
sys.path.append('../..')
from datastructures.stack import Stack
from datastructures.array import ArrayList
from datastructures.patrol_path import PatrolPath
import time
import matplotlib.pyplot as plt

sizes = [100, 1000, 10000, 100000]
array_times = []
linked_times = []

for size in sizes:
  arr = ArrayList()
  path = PatrolPath("one_way")
  start = time.time()
  for i in range(size):
    arr.append(i)
  end = time.time()
  array_times.append(end - start)
  start = time.time()
  for i in range (size):
    path.add_waypoint (i, i)
  end = time.time()
  linked_times.append(end - start)

plt.plot(sizes, array_times, label = "Array List")
plt.plot(sizes, linked_times, label = "Linked List")
plt.xlabel("size")
plt.ylabel("time")
plt.title("Array List vs Linked List")
plt.legend()
plt.show()
