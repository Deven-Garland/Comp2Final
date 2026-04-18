# Graph (final project — you implement).
from datastructures.hash_table import HashTable
from datastructures.array import ArrayList

class Edge:
  def __init__(elf, destination, weight=1):
    self.destination = destination
    self.weight = weight
