from typing import List
from TreeSpecific import TreeGenerator
from circular_array import CircularArray
import random
from MouseCheese import Agent, Grid, Fire, Cheese
import py_trees
import time
import builtins
from MouseCheeseTree import BehaviorTree
import py_trees.display as display
from copy import deepcopy
class Genome:
    genome_counter = 0
    def __init__(self, array: CircularArray = None, tree = None, bb = None, fitness=-1): # defaults for testing
        Genome.genome_counter += 1
        self.id = Genome.genome_counter
        self.fitness = fitness
        self.tree = tree
        self.bb = bb
        self.pArray = None
        self.treeGenerator = TreeGenerator(array) # create behavior tree

    def __deepcopy__(self, memo):
        new_instance = self.__class__(tree=deepcopy(self.tree, memo), fitness=self.fitness)
        new_instance.treeGenerator = self.treeGenerator # NOT for rebuilding..just for reevaluating
        new_instance.pArray = self.pArray[:]
        return new_instance

    def set_up(self):
        size = 5

        # create grid
        g = Grid(size)
        g.grid = [[None for _ in range(size)] for _ in range(size)]
        for i in range(size):
            x = random.randint(0, size-1)
            y = random.randint(0, size-1)
            g.grid[x][y] = Fire(x, y)
        for i in range(size): # cheese could write over a fire
            x = random.randint(0, size-1)
            y = random.randint(0, size-1)
            g.grid[x][y] = Cheese(x, y)

        agent = Agent(False, g)
        g.grid[agent.y][agent.x] = agent

        # fill blackboard
        bbid = str(builtins.id(self)) # randomize namespce based on id
        self.bb = py_trees.blackboard.Client(name=str(self.id), namespace=bbid)
        
        self.bb.register_key(key="g", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="g", access=py_trees.common.Access.READ)

        self.bb.register_key(key="agent", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="agent", access=py_trees.common.Access.READ)

        self.bb.register_key(key="time_start_end", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="time_start_end", access=py_trees.common.Access.READ)

        self.bb.set("g", g)
        self.bb.set("agent", agent)
        self.bb.set("time_start_end", time.time()) # initialize with starting time

    def build_tree(self):
        # used for after crossover: rebuilds tree and sets pArray
        # so that mutation is possible...
        bbid = str(builtins.id(self)) # randomize namespce based on id
        self.bb = py_trees.blackboard.Client(name=str(self.id), namespace=bbid) # dummy

        try: 
            self.tree = self.treeGenerator.generate_tree(self.bb)
            self.pArray = self.treeGenerator.array.convertToList()
        except RecursionError:
            print("build tree recursion error:")
            self.fitness = 0
            self.pArray = [] 
        


    def run_tree(self):
        #CASES:
        # 1. tree is None, fitness == -1, it has never been built before
        # 2. tree is not None, but fitness == -1, so it has been modified: Rerun tree, just don't generate again
        # 3. fitness != -1, it has been built, run & not modified since..return bb
        print("running tree")
        if self.fitness != -1: # case 3: tree unchanged since last run
            assert self.bb != None
            print("no need to rerun tree, returning blackboard")
            return

        self.set_up() # set up blackboard
        self.tree = self.treeGenerator.generate_tree(self.bb) #generate tree or update tree with proper bb
        self.pArray = self.treeGenerator.array.convertToList()

        BT = BehaviorTree(self.bb, self.tree)
        try:
            BT.tick_tree()
        except Exception as e: # TODO: create custom exception
            print(e)
            print("tree was run")
            # TODO: check that is it the correct exception
            return