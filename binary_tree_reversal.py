class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinaryTree:
    def __init__(self, root_value):
        self.root = TreeNode(root_value)

    def insert_left(self, current_node, value):
        if current_node.left is None:
            current_node.left = TreeNode(value)
        else:
            new_node = TreeNode(value)
            new_node.left = current_node.left
            current_node.left = new_node

    def insert_right(self, current_node, value):
        if current_node.right is None:
            current_node.right = TreeNode(value)
        else:
            new_node = TreeNode(value)
            new_node.right = current_node.right
            current_node.right = new_node

    def reverse_tree(self):
        self._reverse_helper(self.root)

    def _reverse_helper(self, node):
        if node is None:
            return
        # Swap left and right children
        node.left, node.right = node.right, node.left
        # Recursively reverse left and right subtrees
        self._reverse_helper(node.left)
        self._reverse_helper(node.right)

# Example usage:
if __name__ == '__main__':
    tree = BinaryTree(1)
    tree.insert_left(tree.root, 2)
    tree.insert_right(tree.root, 3)
    tree.insert_left(tree.root.left, 4)
    tree.insert_right(tree.root.left, 5)

    print('Original Tree:')
    # You can add code to traverse and print the tree here

    tree.reverse_tree()

    print('\nReversed Tree:')
    # You can add code to traverse and print the reversed tree here