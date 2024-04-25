
# File for building a random tree based on a random sequence of number

# <BT> ::= <Selector> | <Sequence>
# <Selector> ::= 'Sel(' <Block> ')'
# <Sequence> ::= 'Seq(' <Block> ')'
# <Block> ::= <Nodes> | <Nodes> ',' <Block>
# <Nodes> ::= <Selector>| <sequence>| 'CondCheese' '(' <DArguments> ')' | 'CondFire' '(' <DArguments> ')' | 'Move' '(' <DArguments> ')'
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

## <Block> ::= <Nodes> | <Nodes> ',' <Block>
    def Block(self):
        choice = self.array.get_element() % 3
        self.index += 1
        if choice == 0 or choice == 1:
            return self.Nodes() # selector or sequence or condition or action
        elif choice == 2:
            return self.BlockAndNodes()

    def BlockAndNodes(self):
        return self.Block() + "," + self.Nodes()

    def Nodes(self):
        choice = self.array.get_element() % 8 # 0-9
        self.index += 1

        if choice == 0:
            return f"CondCheese({self.index-1}, '{self.DArguments()}', bb)"
        elif choice == 1:
            return f"CondFire({self.index-1}, '{self.DArguments()}', bb)"
        elif choice in [2,3]:
            return f"Move({self.index-1}, '{self.DArguments()}', bb)"
        elif choice == 4 or choice == 5:
            return self.SelectorString()
        elif choice == 6 or choice == 7:
            return self.SequenceString()
        

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
            print(self.representationString)
        
        return eval(self.representationString)
