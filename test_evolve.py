import pytest
from typing import List, Tuple
from random import choices, randint, randrange, random
import py_trees.display as display
#from BT_practice.full_agent_tree import Action, Condition
from time import sleep
import py_trees
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from MouseCheeseTree import *
from evolve import find_point, genome_mutate, genome_crossover, prune
import py_trees.display as display
from genome import Genome
from circular_array import CircularArray

# subtree1 = CSelector("Selector", memory=True,children=[Move("left", None)])
# subtree2 = CSequence("Sequence", memory=True, children=[Move("right", None)])
# tree = CSequence("Sequence", memory=True, children=[subtree1, CondCheese("right", None), subtree2])

def test_find_point():
#(self, direction, blackboard)
#CondCheese(Cond
    spot = find_point(tree)
    assert (spot[0] == subtree1 and spot[1] == 0) or (spot[0] == subtree2 and spot[1] == 2) or (spot[0] == tree and spot[1] == -1)

def test_copying_tree():
    b = CSelector("Selector", memory=True,children=[Move("up", None), CondFire("right", None), Move("down", None)])
    tree2 = deepcopy(b)
    display.render_dot_tree(b, name="a_original")
    display.render_dot_tree(tree2, name="a_cross")


def test_prune():
    array = CircularArray([6,2,1,5,7,8,5,4]) # a tree with some unnecessary stuff
    a = Genome(array)

    a.build_tree()
    print("original", a.pArray)
    display.render_dot_tree(a.tree, name="a_original")

    a = prune(a) # alter a genome
    print(a.pArray)
    a.build_tree()
    display.render_dot_tree(a.tree, name="a_pruned")
test_prune() 

def t_single_point_crossover():
    print("I A MRUNNIG THE TEST")
    # not sure how to write tests so currently just doing it visually
    # subtree1 = CSelector("Selector", memory=True,children=[Move("left", None)])
    # subtree2 = CSequence("Sequence", memory=True, children=[Move("right", None)])
    # a = CSequence("Sequence", memory=True, children=[subtree1, CondCheese("right", None), subtree2])
    # b = CSelector("Selector", memory=True,children=[Move("up", None), CondFire("right", None), Move("down", None)])


    a = Genome(CircularArray([0,2,4,6,8,3,4]))
    b = Genome(CircularArray([5,7,9,2,0]))
    a.build_tree()
    b.build_tree()
    display.render_dot_tree(a.tree, name="a_original")
    display.render_dot_tree(b.tree, name="b_original")
    
    newA, newB = genome_crossover(a, b)
    newA.build_tree()
    newB.build_tree()
    
    display.render_dot_tree(newA.tree, name="a_cross")
    display.render_dot_tree(newB.tree, name="b_cross")

# def test_mutation():
#     display.render_dot_tree(tree, name="ORIGINAL")
#     mutation(tree)
#     display.render_dot_tree(tree, name="MUTATED")
