
# File for building a random tree based on a random sequence of number

# <BT> ::= <Selector> | <Sequence>
# <Selector> ::= 'Sel(' <Block> ')'
# <Sequence> ::= 'Seq(' <Block> ')'
# <Block> ::= <Element> | <Element> ',' <Block>
# <Element> ::= <BT> | <Leaf>
# <Leaf> ::= 'CondCheese' '(' <DArguments> ')' | 'CondFire' '(' <DArguments> ')' | 'Move' '(' <DArguments> ')'
# <dArguments> ::=  left|right|up|down
import random
import py_trees.display as display
import time
import py_trees
from MouseCheeseTree import CondCheese, CondFire, Move, BehaviorTree, CSelector, CSequence # nodes for behavior tree
from MouseCheese import Agent, Grid, Fire, Cheese
from circular_array import CircularArray

# CondCheese(direction, blackboard)
# CondFire(direction, blackboard)
# Move(direction, blackboard)

class TreeGenerator:
    def __init__(self, c_list: CircularArray):
        self.array = c_list
        self.representationString = None
        self.index = 0 # index we are in the genome, incremented each time we call get_element

    # Grammar rules
    def BT(self): 
        choice = self.array.get_element() % 2 # 0 or 1
        self.index += 1
        if choice == 0:
            return self.SelectorString()
        else:
            return self.SequenceString()

    def SelectorString(self):
        return f"CSelector('Selector', memory=True, index={self.index-1}, children=[{self.Block()}])"

    def SequenceString(self):
        return f"CSequence('Sequence', memory=True, index={self.index-1}, children=[{self.Block()}])"

    def Block(self):
        choice = self.array.get_element() % 5
        self.index += 1
        if choice == 0:
            return self.BT()
        elif choice == 1:
            return self.BlockAndBT()
        elif choice == 2 or choice == 3:
            return self.Leaf()
        else:
            return self.BlockAndLeaf()

    def BlockAndBT(self):
        return self.Block() + "," + self.BT()

    def BlockAndLeaf(self):
        return self.Block() + "," + self.Leaf()

    def Leaf(self):
        # <Leaf> ::= CondCheese(direction, bb) | CondFire(direction, bb) | Move(direction, bb)
        # artificially make condition 1/3 and actio n2/3
        choice = self.array.get_element() % 6 # 0-5
        self.index += 1
        if choice == 0:
            return f"CondCheese({self.index-1}, '{self.DArguments()}', bb)"
        elif choice == 1:
            return f"CondFire({self.index-1}, '{self.DArguments()}', bb)"
        else:
            return f"Move({self.index-1}, '{self.DArguments()}', bb)"

    def DArguments(self): 
        choice = self.array.get_element() % 4 # 0, 1, 2, 3
        self.index += 1
        if choice == 0:
            return "left"
        elif choice == 1:
            return "right"
        elif choice == 2:
            return "up"
        else:
            return "down"

    # Generate a string using the grammar
    def generate_tree(self, bb):
        if self.representationString is None:
            self.index = 0 # reset before making
            self.representationString = self.BT()
        
        return eval(self.representationString)
