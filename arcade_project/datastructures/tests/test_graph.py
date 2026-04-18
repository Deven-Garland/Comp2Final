"""
test_graph.py - test for Binary Search Tree Implementation 

Run from the project root:
    python datastructures/tests/test_graph.py

Author: Mennah Khaled Dewidar
Date: 4/17/2026
Computation Final Project
"""
import sys
sys.path.append('..')  # Add parent directory to path
from graph import Graph, Edge
 
 
def test_graph_creation():
    """Test creating a Graph"""
    print("Testing Graph creation...")
 
    graph = Graph()
    assert graph.adj_list is not None
 
    print("✓ Graph creation works!")
 
 
def test_add_vertex():
    graph = Graph()
    graph.add_vertex("A")
    assert graph.adj_list.get("A") is not None
    print("✓ Graph add_vertex works!")
 
 
def test_add_vertex_no_duplicate():
    graph = Graph()
    graph.add_vertex("A")
    graph.add_vertex("A")
    neighbors = graph.adj_list.get("A")
    assert len(neighbors) == 0
    print("✓ Graph add_vertex no duplicate works!")
 
 
def test_add_edge():
    graph = Graph()
    graph.add_edge("A", "B")
    assert graph.has_edge("A", "B")
    print("✓ Graph add_edge works!")
 
 
def test_add_edge_creates_vertices():
    graph = Graph()
    graph.add_edge("A", "B")
    assert graph.adj_list.get("A") is not None
    assert graph.adj_list.get("B") is not None
    print("✓ Graph add_edge creates vertices works!")
 
 
def test_add_edge_with_weight():
    graph = Graph()
    graph.add_edge("A", "B", weight=5)
    neighbors = graph.get_neighbors("A")
    assert neighbors[0].weight == 5
    print("✓ Graph add_edge with weight works!")
 
 
def test_add_edge_no_duplicate():
    graph = Graph()
    graph.add_edge("A", "B")
    graph.add_edge("A", "B")
    neighbors = graph.get_neighbors("A")
    assert len(neighbors) == 1
    print("✓ Graph add_edge no duplicate works!")
 
 
def test_get_neighbors():
    graph = Graph()
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    neighbors = graph.get_neighbors("A")
    assert len(neighbors) == 2
    print("✓ Graph get_neighbors works!")
 
 
def test_get_neighbors_none():
    graph = Graph()
    assert graph.get_neighbors("A") is None
    print("✓ Graph get_neighbors returns None for missing vertex works!")
 
 
def test_has_edge_true():
    graph = Graph()
    graph.add_edge("A", "B")
    assert graph.has_edge("A", "B")
    print("✓ Graph has_edge true works!")
 
 
def test_has_edge_false():
    graph = Graph()
    graph.add_edge("A", "B")
    assert graph.has_edge("B", "A") == False
    print("✓ Graph has_edge false works!")
 
 
def test_has_edge_missing_vertex():
    graph = Graph()
    assert graph.has_edge("X", "Y") == False
    print("✓ Graph has_edge missing vertex works!")
 
 
def test_remove_edge():
    graph = Graph()
    graph.add_edge("A", "B")
    graph.remove_edge("A", "B")
    assert graph.has_edge("A", "B") == False
    print("✓ Graph remove_edge works!")
 
 
def test_remove_edge_missing():
    graph = Graph()
    graph.add_vertex("A")
    graph.remove_edge("A", "B")
    assert graph.has_edge("A", "B") == False
    print("✓ Graph remove_edge missing edge works!")
 
 
def test_remove_edge_missing_vertex():
    graph = Graph()
    graph.remove_edge("X", "Y")
    print("✓ Graph remove_edge missing vertex works!")
 
 
def test_get_vertices():
    graph = Graph()
    graph.add_vertex("A")
    graph.add_vertex("B")
    graph.add_vertex("C")
    vertices = graph.get_vertices()
    assert len(vertices) == 3
    print("✓ Graph get_vertices works!")
 
 
def test_get_vertices_empty():
    graph = Graph()
    vertices = graph.get_vertices()
    assert len(vertices) == 0
    print("✓ Graph get_vertices empty works!")
 
 
# Edge cases:
def test_edge_eq():
    # the purpose of this edge case is to test that two edges with the same
    # destination and weight are considered equal, which is needed for remove to work
    edge1 = Edge("B", 1)
    edge2 = Edge("B", 1)
    assert edge1 == edge2
    print("✓ Edge __eq__ works!")
 
 
def test_edge_eq_different_weight():
    # the purpose of this edge case is to test that two edges with the same
    # destination but different weights are NOT considered equal
    edge1 = Edge("B", 1)
    edge2 = Edge("B", 5)
    assert edge1 != edge2
    print("✓ Edge __eq__ different weight works!")
 
 
def test_add_multiple_edges():
    # the purpose of this edge case is to test adding many edges from one vertex
    # and confirming all neighbors are stored correctly
    graph = Graph()
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("A", "D")
    neighbors = graph.get_neighbors("A")
    assert len(neighbors) == 3
    assert graph.has_edge("A", "B")
    assert graph.has_edge("A", "C")
    assert graph.has_edge("A", "D")
    print("✓ Edge cases for multiple edges work!")
 
 
def test_remove_one_of_many_edges():
    # the purpose of this edge case is to test that removing one edge
    # does not affect the other edges from the same vertex
    graph = Graph()
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("A", "D")
    graph.remove_edge("A", "C")
    assert graph.has_edge("A", "B")
    assert graph.has_edge("A", "C") == False
    assert graph.has_edge("A", "D")
    print("✓ Edge cases for remove one of many edges work!")
 
 
def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("Running Graph Tests")
    print("="*50)
 
    test_graph_creation()
    test_add_vertex()
    test_add_vertex_no_duplicate()
    test_add_edge()
    test_add_edge_creates_vertices()
    test_add_edge_with_weight()
    test_add_edge_no_duplicate()
    test_get_neighbors()
    test_get_neighbors_none()
    test_has_edge_true()
    test_has_edge_false()
    test_has_edge_missing_vertex()
    test_remove_edge()
    test_remove_edge_missing()
    test_remove_edge_missing_vertex()
    test_get_vertices()
    test_get_vertices_empty()
 
    test_edge_eq()
    test_edge_eq_different_weight()
    test_add_multiple_edges()
    test_remove_one_of_many_edges()
 
    print("="*50)
    print("✓ ALL TESTS PASSED!")
    print("="*50)
 
 
if __name__ == "__main__":
    run_all_tests()