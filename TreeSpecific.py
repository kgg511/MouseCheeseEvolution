
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

    # Grammar rules
    def BT(self): 
        choice = self.array.get_element() % 2 # 0 or 1
        if choice == 0:
            return self.SelectorString()
        else:
            return self.SequenceString()

    def SelectorString(self):
        return "CSelector('Selector', memory=True, children=[" + self.Block() + "])"

    def SequenceString(self):
        return "CSequence('Sequence', memory=True, children=[" + self.Block() + "])"

    #<Block> ::= <Element> | <Element> ',' <Block>
    # def Block(self):
    #     print("Block")
    #     choice = self.array.get_element() % 2 
    #     if choice == 0:
    #         return self.Element()
    #     else:
    #         return self.Element() + "," + self.Block()

    # def Element(self):
    #     print("Element")
    #     choice = self.array.get_element() % 2 # 0 - 3
    #     if choice == 1:
    #         return self.BT()
    #     else:
    #         return self.Leaf()

    def Block(self):
        choice = self.array.get_element() % 5
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
        if choice == 0:
            return f"CondCheese('{self.DArguments()}', bb)"
        elif choice == 1:
            return f"CondFire('{self.DArguments()}', bb)"
        else: # 2-5 aka 2/3 chance
            return f"Move('{self.DArguments()}', bb)"

    def DArguments(self): 
        choice = self.array.get_element() % 4 # 0, 1, 2, 3
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
            self.representationString = self.BT()
        
        print(self.representationString)
        return eval(self.representationString)

