# code/datastructures/tests/bst_tests.py
import sys
sys.path.append('..')  # Add parent directory to path
from bst import BinarySearchTree


def test_bst_creation():
    """Test creating a BinarySearchTree"""
    print("Testing BinarySearchTree creation...")

    bst = BinarySearchTree()
    assert bst.root is None, "New BST should have no root"

    print("✓ BinarySearchTree creation works!")


def test_insert():
    bst = BinarySearchTree()
    bst.insert(10)
    assert bst.root.value == 10
    bst.insert(5)
    assert bst.root.left_node.value == 5
    bst.insert(15)
    assert bst.root.right_node.value == 15
    print("✓ BST insert works!")


def test_search():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    assert bst.search(10).value == 10
    assert bst.search(5).value == 5
    assert bst.search(99) is None
    print("✓ BST search works!")


def test_delete():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    bst.delete(5)
    assert bst.search(5) is None
    assert bst.search(10) is not None
    print("✓ BST delete works!")


def test_traverse_inorder():
    bst = BinarySearchTree()
    bst.insert(20)
    bst.insert(10)
    bst.insert(30)
    result = {0: 0}
    bst.traverse("in", bst.root, result)
    assert result[1] == 10
    assert result[2] == 20
    assert result[3] == 30
    print("✓ BST inorder traversal works!")


def test_traverse_preorder():
    bst = BinarySearchTree()
    bst.insert(20)
    bst.insert(10)
    bst.insert(30)
    result = {0: 0}
    bst.traverse("pre", bst.root, result)
    assert result[1] == 20
    assert result[2] == 10
    assert result[3] == 30
    print("✓ BST preorder traversal works!")


def test_traverse_postorder():
    bst = BinarySearchTree()
    bst.insert(20)
    bst.insert(10)
    bst.insert(30)
    result = {0: 0}
    bst.traverse("post", bst.root, result)
    assert result[1] == 10
    assert result[2] == 30
    assert result[3] == 20
    print("✓ BST postorder traversal works!")


def test_is_empty():
    bst = BinarySearchTree()
    assert bst.is_empty() == True
    bst.insert(1)
    assert bst.is_empty() == False
    print("✓ BST is_empty works!")


def test_get_size():
    bst = BinarySearchTree()
    assert bst.get_size(bst.root) == 0
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    assert bst.get_size(bst.root) == 3
    print("✓ BST get_size works!")


def test_get_height():
    bst = BinarySearchTree()
    assert bst.get_height(bst.root) == -1
    bst.insert(10)
    assert bst.get_height(bst.root) == 0
    bst.insert(5)
    bst.insert(15)
    assert bst.get_height(bst.root) == 1
    print("✓ BST get_height works!")


def test_get_min():
    bst = BinarySearchTree()
    assert bst.get_min() is None
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    assert bst.get_min() == 5
    print("✓ BST get_min works!")


def test_get_max():
    bst = BinarySearchTree()
    assert bst.get_max() is None
    bst.insert(10)
    bst.insert(5)
    bst.insert(15)
    assert bst.get_max() == 15
    print("✓ BST get_max works!")


def test_get_predecessor():
    bst = BinarySearchTree()
    bst.insert(20)
    bst.insert(10)
    bst.insert(30)
    bst.insert(5)
    assert bst.get_predecessor(10) == 5
    assert bst.get_predecessor(20) == 10
    assert bst.get_predecessor(5) is None
    print("✓ BST get_predecessor works!")


def test_str():
    bst = BinarySearchTree()
    bst.insert(20)
    bst.insert(10)
    bst.insert(30)
    assert str(bst) == "[10 20 30]"
    print("✓ BST __str__ works!")


def test_clear():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.clear()
    assert bst.root is None
    assert bst.is_empty() == True
    print("✓ BST clear works!")


# Edge cases:
def test_insert_edge():
    # the purpose of this edge case is to test that duplicate values are ignored
    # and that values are placed on the correct side of the tree
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(10)
    assert bst.get_size(bst.root) == 1, "Duplicate values should be ignored"
    bst.insert(5)
    bst.insert(15)
    assert bst.root.left_node.value == 5, "Smaller value should go left"
    assert bst.root.right_node.value == 15, "Larger value should go right"
    print("✓ Edge cases for insert work!")


def test_delete_edge():
    # the purpose of this edge case is to test all three deletion scenarios:
    # deleting a leaf, a node with one child, and a node with two children
    bst = BinarySearchTree()
    bst.insert(20)
    bst.insert(10)
    bst.insert(30)
    bst.insert(5)
    bst.insert(15)

    # delete leaf node
    bst.delete(5)
    assert bst.search(5) is None

    # delete node with one child
    bst.delete(10)
    assert bst.search(10) is None
    assert bst.search(15) is not None

    # delete node with two children
    bst.delete(20)
    assert bst.search(20) is None
    assert bst.search(30) is not None

    # delete value that does not exist
    bst.delete(999)
    assert bst.get_size(bst.root) == 2

    print("✓ Edge cases for delete work!")


def test_search_edge():
    # the purpose of this edge case is to test searching in an empty tree
    # and searching for a value that does not exist
    bst = BinarySearchTree()
    assert bst.search(10) is None, "Search in empty tree should return None"
    bst.insert(10)
    assert bst.search(99) is None, "Search for missing value should return None"
    print("✓ Edge cases for search work!")


def test_get_height_edge():
    # the purpose of this edge case is to test height on a skewed tree
    # where every node only has a right child, making it essentially a linked list
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(20)
    bst.insert(30)
    bst.insert(40)
    assert bst.get_height(bst.root) == 3, "Skewed tree of 4 nodes should have height 3"
    print("✓ Edge cases for get_height work!")


def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("Running BinarySearchTree Tests")
    print("="*50)

    test_bst_creation()
    test_insert()
    test_search()
    test_delete()
    test_traverse_inorder()
    test_traverse_preorder()
    test_traverse_postorder()
    test_is_empty()
    test_get_size()
    test_get_height()
    test_get_min()
    test_get_max()
    test_get_predecessor()
    test_str()
    test_clear()

    test_insert_edge()
    test_delete_edge()
    test_search_edge()
    test_get_height_edge()

    print("="*50)
    print("✓ ALL TESTS PASSED!")
    print("="*50)


if __name__ == "__main__":
    run_all_tests()