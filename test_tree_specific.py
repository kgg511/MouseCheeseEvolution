
# test that the proper index is being stored n a tree
from TreeSpecific import TreeGenerator
from circular_array import CircularArray
import py_trees.display as display
from genome import Genome
def test_tree_index():
    #array = CircularArray([0, 1, 2, 3, 4, 5])

    array = CircularArray([0,2,4,6,8,3,4,8,2,4,1,3,4,2,5,6,7,8,6,4,6,7,5,3,3,5])
    genome = Genome(array)
    genome.build_tree()

    display.render_dot_tree(genome.tree, name="a_original")

    

test_tree_index()