import pytest
from circular_array import CircularArray
from TreeSpecific import TreeGenerator
from MouseCheese import Agent, Grid, Fire, Cheese
import py_trees
import py_trees.display as display
import random
@pytest.fixture 
def circular_array():
    items = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    return CircularArray(items)

def test_get_element(circular_array):
    assert circular_array.length == 0
    for i in range(15):
        circular_array.get_element()
    assert circular_array.length == 15

def test_convert_to_list(circular_array):
    for i in range(15):
        circular_array.get_element()
    assert circular_array.convertToList() == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 1, 2, 3]

def test_index(circular_array):
    for i in range(15):
        circular_array.get_element()
    assert circular_array.get(11) == 0

    with pytest.raises(IndexError) as e:
        circular_array.get(15)

# how have not ACTUALLY TESTED USING IT TO MAKE TREE
import sys

def test_making_tree(): # also a way to test if your circular array has a good nubmer of stuff
    sys.setrecursionlimit(2000)
    bb = py_trees.blackboard.Blackboard()
    array = [0,6,3,2,9,8,2,3,1,0,0,5,9]
    array = [random.randint(0,9) for _ in range(200)]
    gen = TreeGenerator(CircularArray(array))
    tree = gen.generate_tree(bb)
    display.render_dot_tree(tree, name="behavior_tree_test")
