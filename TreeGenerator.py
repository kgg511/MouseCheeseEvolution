
# File for building a random tree based on a random sequence of number

# <BT> ::= <Selector> | <Sequence>
# <Selector> ::= 'Sel(' <Block> ')'
# <Sequence> ::= 'Seq(' <Block> ')'
# <Block> ::= <BT> | <Block> ',' <BT>  | <Leaf> | <Block> ',' <Leaf>
# <Leaf> ::= 'Action' '(' <AArguments> ')' | 'Condition' '(' <CArguments> ')'
# <CArguments> ::= cheese <dArguments> | fire <dArguments>
# <dArguments> ::=  left|right|up|down
import random
import py_trees.display as display
#from BT_practice.full_agent_tree import Action, Condition
from time import sleep
import py_trees
from py_trees.behaviour import Behaviour
from py_trees.common import Status

class Action(Behaviour):
    def __init__(self, name):
        super(Action, self).__init__(name)

    def setup(self):
        self.logger.debug(f"Action::setup {self.name}")

    def initialise(self):
        self.attempt_count = self.max_attempt_count
        self.logger.debug(f"Action::initialise {self.name}")

    def update(self):
        self.attempt_count -= 1
        self.logger.debug(f"Action::update {self.name}")
        sleep(1)
        if not self.attempt_count:
            return Status.SUCCESS
        return Status.RUNNING

    def terminate(self, new_status):
        self.logger.debug(f"Action::terminate {self.name} to {new_status}")


class Condition(Behaviour):
    def __init__(self, name):
        super(Condition, self).__init__(name)

    def setup(self):
        self.logger.debug(f"Condition::setup {self.name}")

    def initialise(self):
        self.logger.debug(f"Condition::initialise {self.name}")

    def update(self):
        self.logger.debug(f"Condition::update {self.name}")
        sleep(1)
        return Status.SUCCESS

    def terminate(self, new_status):
        self.logger.debug(f"Condition::terminate {self.name} to {new_status}")



#######################
# Grammar rules
def BT(num_list):
    choice = num_list[0] % 2 # 0 or 1
    if choice == 0:
        return SelectorString(num_list[1:])
    else:
        return SequenceString(num_list[1:])

def SelectorString(num_list):
    return "CSelector('Selector', memory=True, children=[" + Block(num_list[1:]) + "])"

def SequenceString(num_list):
    return "CSequence('Sequence', memory=True, children=[" + Block(num_list[1:]) + "])"

def Block(num_list):
    choice = num_list[0] % 4 # 0, 1, 2, 3
    if choice == 0:
        return BT(num_list[1:])
    elif choice == 1:
        return BlockAndBT(num_list[1:])
    elif choice == 2:
        return Leaf(num_list[1:])
    else:
        return BlockAndLeaf(num_list[1:])

def BlockAndBT(num_list):
    return Block(num_list[1:]) + "," + BT(num_list[1:])

def BlockAndLeaf(num_list):
    return Block(num_list[1:]) + "," + Leaf(num_list[1:])

def Leaf(num_list):
    # <Leaf> ::= 'Action' '(' <AArguments> ')' | 'Condition' '(' <CArguments> ')'
    choice = num_list[0] % 2 # 0 or 1
    if choice == 0:
        return f"Action('{DArguments(num_list[1:])}')"
    else:
        return f"Condition('{CArguments(num_list[1:])}?')"

def CArguments(num_list): # arguments that only apply to conditions
    choice = num_list[0] % 2 # 0 or 1
    if choice == 0:
        return f"cheese {DArguments(num_list[1:])}"
    else:
        return f"fire {DArguments(num_list[1:])}"


def DArguments(num_list): 
    choice = num_list[0] % 4 # 0, 1, 2, 3
    if choice == 0:
        return "left"
    elif choice == 1:
        return "right"
    elif choice == 2:
        return "up"
    else:
        return "down"

# Generate a string using the grammar
def generate_tree(num_list):
    treeString = BT(num_list)
    print(treeString)
    return eval(treeString)

#failed = Sequence("Sequence1", memory=True, children=[Condition("State=Failed"), Action("Update state variable"), Action("Failed")])
#root = (Selector("Selector", memory=True, children=[observe, explore, assess, returnm, dance, helper, travel, failed]))

def create_genome():
    return [random.randint(0,9) for _ in range(100)]

# Example usage
if __name__ == "__main__":

    genome = create_genome() # list of numbers
    tree = generate_tree(genome)

    display.render_dot_tree(tree, name="behavior_tree")


    # for _ in range(5):  # Generate 5 strings
    #     print(generate_string())



