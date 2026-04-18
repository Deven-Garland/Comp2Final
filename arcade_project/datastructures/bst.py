"""
bst.py - Dynamic Array Implementation

I implemented a dynamic binary search tree (like Python's list) from scratch.
This will be used throughout the course in place of built-in lists.

Author: Mennah Khaled Dewidar
Date: 4/17/2026
Computation Final Project
"""
class Node:
    """
    Implement the methods discussed here:
    https://www.geeksforgeeks.org/python/binary-search-tree-in-python/
    Creating a node class for basic structure
    """
 
    def __init__(self, value):
        """
        instance variables needed: the value stored, left and right node which is initially empty
        """
        self.value = value
        self.left_node = None
        self.right_node = None
 
 
class BinarySearchTree:
    """
    a BST where left subtree values are smaller than the root and right subtree values
    are greater than the root
    """
 
    def __init__(self):
        """
        instance variables needed: the root of the tree which is initially empty
        """
        self.root = None
 
    def insert(self, value):
        """
        inserts a new value into the correct position in the BST using a loop
        - left if the value is smaller, right if larger, until an empty spot is found
        ignoring duplicate values
        """
        new_node = Node(value)
        if self.root is None:
            self.root = new_node
            return
 
        current = self.root
        while current is not None:
            if value == current.value:
                return
 
            if value < current.value:
                if current.left_node is None:
                    current.left_node = new_node
                    return
                current = current.left_node
 
            else:
                if current.right_node is None:
                    current.right_node = new_node
                    return
                current = current.right_node
 
    def search(self, value):
        """
        searches for a value in BST starting from the root
        returns the node containing the value, or None if it does not exist
        """
        current = self.root
        while current is not None:
            if value == current.value:
                return current
            if value < current.value:
                current = current.left_node
            else:
                current = current.right_node
        return None
 
    def delete(self, value):
        """
        deletes the node with the given value from the BST
        - case 1: leaf node (no children) just remove it
        - case 2: one child, replace node with that child
        - case 3: two children, find the next largest value (smallest in right subtree) to replace it
        """
        parent = None
        current = self.root
        while current is not None and current.value != value:
            parent = current
            if value < current.value:
                current = current.left_node
            else:
                current = current.right_node
        if current is None:
            return
 
        if current.left_node is not None and current.right_node is not None:
            next_largest_parent = current
            next_largest = current.right_node
            while next_largest.left_node is not None:
                next_largest_parent = next_largest
                next_largest = next_largest.left_node
            current.value = next_largest.value
            current = next_largest
            parent = next_largest_parent
        if current.left_node is not None:
            child = current.left_node
        else:
            child = current.right_node
        if parent is None:
            self.root = child
        elif parent.left_node == current:
            parent.left_node = child
        else:
            parent.right_node = child
 
    def inorder(self, node, result):
        """
        sorting from smallest to largest values
        """
        if node is None:
            return
        self.inorder(node.left_node, result)
        result[0] = result[0] + 1
        result[result[0]] = node.value
        self.inorder(node.right_node, result)
 
    def is_empty(self):
        """
        checks if the BST has no nodes by checking if the root is empty
        """
        if self.root is None:
            return True
        return False
 
    def get_size(self, node):
        """
        counts and returns the total number of nodes in the BST
        if the node is None we have reached an empty spot so we return 0
        otherwise we count this node (1) plus all nodes to the left and right
        """
        if node is None:
            return 0
        left_count = self.get_size(node.left_node)
        right_count = self.get_size(node.right_node)
        total = 1 + left_count + right_count
        return total
 
    def get_height(self, node):
        """
        returns the height of the BST which is the longest path from root to a leaf
        returns -1 if empty, 0 if only a root
        """
        if node is None:
            return -1
        left_height = self.get_height(node.left_node)
        right_height = self.get_height(node.right_node)
        if left_height > right_height:
            return 1 + left_height
        return 1 + right_height
 
    def get_min(self):
        """
        returns the smallest value by walking left until there is no left child
        returns None if the tree is empty
        """
        if self.root is None:
            return None
        current = self.root
        while current.left_node is not None:
            current = current.left_node
        return current.value
 
    def get_max(self):
        """
        returns the largest value by walking right until there is no right child
        returns None if the tree is empty
        """
        if self.root is None:
            return None
        current = self.root
        while current.right_node is not None:
            current = current.right_node
        return current.value
 
    def __str__(self):
        """
        returns a user-friendly string representation when you call str(bst) or print(bst)
        """
        result = {0: 0}
        self.inorder(self.root, result)
        output = "["
        i = 1
        while i <= result[0]:
            output += str(result[i])
            if i != result[0]:
                output += ", "
            i = i + 1
        output += "]"
        return output
 
    def __repr__(self):
        """
        returns a developer-friendly string representation (often the same as __str__ for simple classes), used in the interactive shell
        """
        return self.__str__()
 
    # Makes the BST iterable so you can use it in for loops: for item in my_bst:
    def __iter__(self):
        """
        makes the BST iterable so you can use it in for loops: for item in my_bst:
        visits values in ascending sorted order using inorder traversal
        """
        result = {0: 0}
        self.inorder(self.root, result)
        i = 1
        while i <= result[0]:
            yield result[i]
            i = i + 1
 
    def clear(self):
        """
        removes all nodes from the BST by resetting the root to None
        """
        self.root = None