# Graph (final project — you implement).
from datastructures.hash_table import HashTable
from datastructures.array import ArrayList

class Edge:
    def __init__(self, destination, weight=1):
        self.destination = destination
        self.weight = weight

    def __eq__(self, other):
        # Needed so ArrayList.remove() works correctly
        return (
            isinstance(other, Edge)
            and self.destination == other.destination
            and self.weight == other.weight
        )

class Graph:
    def __init__(self):
        # key: vertex
        # value: ArrayList of Edge objects
        self.adj_list = HashTable()

    def add_vertex(self, vertex):
        if self.adj_list.get(vertex) is None:
            self.adj_list.put(vertex, ArrayList())

    def add_edge(self, src, dest, weight=1):
        # ensure both vertices exist
        self.add_vertex(src)
        self.add_vertex(dest)

        neighbors = self.adj_list.get(src)

        # prevent duplicate edges (optional but good)
        for edge in neighbors:
            if edge.destination == dest:
                return

        neighbors.append(Edge(dest, weight))

    def get_neighbors(self, vertex):
        return self.adj_list.get(vertex)

    def has_edge(self, src, dest):
        neighbors = self.adj_list.get(src)
        if neighbors is None:
            return False

        for edge in neighbors:
            if edge.destination == dest:
                return True

        return False

    def remove_edge(self, src, dest):
        neighbors = self.adj_list.get(src)
        if neighbors is None:
            return

        # find mathcing edge
        for edge in neighbors:
            if edge.destination == dest:
                neighbors.remove(edge)  # remove by value (your implementation)
                return

    def get_vertices(self):
        # uses your __iter__ in HashTable
        vertices = ArrayList()
        for key in self.adj_list:
            vertices.append(key)
        return vertices
