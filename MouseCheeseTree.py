import py_trees
import random
from MouseCheese import Cheese, Agent, Grid, Fire
import time
import py_trees.display as display

import time
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from py_trees import logging as log_tree
from typing import Callable as function
from copy import deepcopy
time_trial = 10

class CSequence(py_trees.composites.Sequence):
    def __init__(self, name=None, memory=False, children=None, index=-1):
        # Call the __init__() method of the base class with the required arguments
        super().__init__(name=name, memory=memory, children=children)
        self.index = index # index of genome used to make this
    def remove_parent(self):
        self.parent = None
    def __deepcopy__(self, memo):
        #copy children
        new_children = [deepcopy(child, memo) for child in self.children]
        # Create a new instance of CustomSequence
        new_instance = self.__class__(name=self.name, memory=self.memory, children=new_children)
        # Return the new instance
        return new_instance

class CSelector(py_trees.composites.Selector):
    def __init__(self, name=None, memory=False, children=None, index=-1):
        # Call the __init__() method of the base class with the required arguments
        super().__init__(name=name, memory=memory, children=children)
        self.index = index # index of genome used to make this
    def remove_parent(self):
        self.parent = None
    def __deepcopy__(self, memo):
        # Create a new instance of CustomSelector
        new_children = [deepcopy(child, memo) for child in self.children]
        new_instance = self.__class__(name=self.name, memory=self.memory, children=new_children)
        # Return the new instance
        return new_instance

class Node(py_trees.behaviour.Behaviour):
    def __init__(self, name, blackboard, index=-1):
        super().__init__(name)
        self.blackboard = blackboard
        self.parent = None  # Parent node
        self.index = index # index of genome used to make this
    def checkTime(self):
        agent = self.blackboard.get("agent")
        timePassed = time.time() - agent.timeStart
        if not agent.dead and timePassed > time_trial:
            agent.trialTime = timePassed
            raise Exception("Time's up")
        elif agent.dead:
            raise Exception("Agent dead")
        
    def remove_parent(self):
        self.parent = None

# Actions: move left, right, up, down
#condtions: fire/cheese left/right/up/down

# success if cheese in specified spot, else failure
# also failure if mouse is dead
class Cond(Node): # look for cheese/fire left/right/up/down
    def __init__(self, name, direction, lookFor, blackboard, index=-1):
        super().__init__(name, blackboard, index) #f"Cheese {direction}?"
        self.direction = direction # left, right, up, down
        self.blackboard = blackboard
        self.lookFor = lookFor # cheese, fire
    def update(self):
        self.checkTime()
        agent = self.blackboard.get("agent")
        gridObject = self.blackboard.get("g")
        #print(f"Checking {self.direction} for {self.lookFor}")
        #gridObject.printGrid()
        
        #time.sleep(2)

        if agent.dead:
            return py_trees.common.Status.FAILURE
        elif self.checkSpot(): # the item is there -> success
            return py_trees.common.Status.SUCCESS       
        
        return py_trees.common.Status.FAILURE # not there
    
    def checkSpot(self):
        agent = self.blackboard.get("agent")
        gridObject = self.blackboard.get("g")
        if self.direction == "left":
            if agent.x - 1 < 0:
                return False
            return isinstance(gridObject.grid[agent.y][agent.x - 1], self.lookFor)
        elif self.direction == "right":
            if agent.x + 1 >= gridObject.size:
                return False
            return isinstance(gridObject.grid[agent.y][agent.x + 1], self.lookFor)
        elif self.direction == "up":
            if agent.y - 1 < 0:
                return False
            return isinstance(gridObject.grid[agent.y - 1][agent.x], self.lookFor)
        elif self.direction == "down":
            if agent.y + 1 >= gridObject.size:
                return False
            return isinstance(gridObject.grid[agent.y + 1][agent.x], self.lookFor)  
    

# (self, name, direction, lookFor, blackboard)
class CondCheese(Cond): 
    def __init__(self, index, direction, blackboard):
        super().__init__(f"Cheese {direction}?", direction, Cheese, blackboard, index)
    
    def __deepcopy__(self, memo):
        return self.__class__(self.direction, self.blackboard)

class CondFire(Cond): 
    def __init__(self, index, direction, blackboard):
        super().__init__(f"Fire {direction}?", direction, Fire, blackboard, index)
    def __deepcopy__(self, memo):
        return self.__class__(self.direction, self.blackboard)

# moves agent
class Move(Node):
    def __init__(self, index, direction, blackboard):
        super().__init__(f"Move {direction}", blackboard, index)
        self.direction = direction # left, right, up, down
        self.blackboard = blackboard
    def __deepcopy__(self, memo):
        return self.__class__(self.direction, self.blackboard)
    def update(self):
        self.checkTime()
        agent = self.blackboard.get("agent")
        gridObject = self.blackboard.get("g")
        self.move(agent)        
        if agent.dead:
            return py_trees.common.Status.FAILURE

        #print(f"Moved {self.direction}")
        #gridObject.printGrid()
        
        #time.sleep(2)
        return py_trees.common.Status.SUCCESS    
    
    def move(self, agent):
        if self.direction == "left" and agent.x - 1 >= 0:
            agent.move(agent.x - 1, agent.y)
        elif self.direction == "right" and agent.x + 1 < agent.grid.size:
            agent.move(agent.x + 1, agent.y)
        elif self.direction == "up" and agent.y - 1 >= 0:
            agent.move(agent.x, agent.y - 1)
        elif self.direction == "down" and agent.y + 1 < agent.grid.size:
            agent.move(agent.x, agent.y + 1)

class BehaviorTree():
    # contains all stuff we want to do with the tree
    # create 2d grid of random Food() and None of size 10x10
    # blackboard variable contains grid, agent
    def __init__(self, blackboard, root):
        assert blackboard is not None
        self.blackboard = blackboard
        self.tree = self.make_bt(root)
        
    def make_bt(self, root): #not used
        return py_trees.trees.BehaviourTree(root)

    def tick_tree(self):
        # Tick the Behavior Tree to execute it
        for i in range(5):  # Repeat the sequence 5 times
            self.tree.tick_tock(
                period_ms=5 # wait 5 ms between ticks 
            )
            #self.blackboard.get("g").printGrid()


    