
# test that the proper index is being stored n a tree
from TreeSpecific import TreeGenerator
from circular_array import CircularArray

def test_tree_index():
    array = CircularArray([0, 1, 2, 3, 4, 5])
    generator = TreeGenerator(array)
    print(generator.BT())

