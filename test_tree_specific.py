
# test that the proper index is being stored n a tree
from TreeSpecific import TreeGenerator
from circular_array import CircularArray
import py_trees.display as display
from genome import Genome
def test_tree_index():
    #array = CircularArray([0, 1, 2, 3, 4, 5])

    array = CircularArray([2,1,5,7,6,5])
    genome = Genome(array)
    genome.build_tree()

    display.render_dot_tree(genome.tree, name="a_original")



test_tree_index()