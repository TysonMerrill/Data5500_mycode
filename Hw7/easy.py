import random
import time
from print_tree import *

class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

def insert(node, key):
    if node is None:
        return Node(key)
    if key < node.key:
        node.left = insert(node.left, key)
    else:
        node.right = insert(node.right, key)
    return node

def findMin(node):
    while node.left is not None:
        node = node.left
    return node

def findMinRec(node):
    if node.left is None:
        return node
    return findMinRec(node.left)

def findMaxRec(node):
    if node.right is None:
        return node
    return findMaxRec(node.right)

def inorder(root):
    if root is not None:
        inorder(root.left)
        print(root.key, end=" ")
        inorder(root.right)

def preorder(root):
    if root is not None:
        print(root.key, end=" ")
        preorder(root.left)
        preorder(root.right)

def postorder(root):
    if root is not None:
        postorder(root.left)
        postorder(root.right)
        print(root.key, end=" ")

def findKey(root, searchkey):
    if searchkey < root.key:
        if root.left is None:
            return str(searchkey) + " Not Found"
        return findKey(root.left, searchkey)
    elif searchkey > root.key:
        if root.right is None:
            return str(searchkey) + " Not Found"
        return findKey(root.right, searchkey)
    else:
        return str(root.key) + ' is found'

def main():
    root = None
    root = insert(root, 55)
    root = insert(root, 66)
    root = insert(root, 27)
    root = insert(root, 38)
    root = insert(root, 37)
    root = insert(root, 84)
    root = insert(root, 67)
    
    print("Inorder traversal of the given tree")
    inorder(root)
    print()
    display(root)
    
main()
