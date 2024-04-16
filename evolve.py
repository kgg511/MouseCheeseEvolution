
from typing import List, Tuple
from random import choices, randint, randrange, random
from collections import namedtuple
from typing import List, Callable
from functools import partial
import time
from typing import Union
import random
import time
import py_trees
from MouseCheeseTree import BehaviorTree, Node, CondCheese, CondFire, Move # nodes for behavior tree
from MouseCheese import Agent, Grid, Fire, Cheese
from circular_array import CircularArray
from genome import Genome
from TreeSpecific import TreeGenerator
from copy import deepcopy
import sys
import py_trees.display as display

Population = List[Genome]
FitnessFunc = Callable[[Genome], int] # how good genome is
PopulateFunc = Callable[[], Population]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]

# selection_pair(population: Population, fitness_func: FitnessFunc, blackboard) 
Thing = namedtuple('Thing', ['name', 'value', 'weight']) # instead make this a behavior tree
things = [
    Thing('Laptop', 500, 2200),
    Thing('Headphones', 150, 160),
    Thing('Coffee Mug', 60, 350),
    Thing('Notepad', 40, 333),
    Thing('Water Bottle', 30, 192),
]

def generate_genome(length: int) -> Genome:
    numbers = [random.randint(0,9) for _ in range(length)] # length of circular array
    array = CircularArray(numbers)
    return Genome(array)

def generate_population(size:int, genome_length: int)-> Population: # originally al the same length before made into trees
    return [generate_genome(genome_length) for _ in range(size)] # list of lists

def fitness(genome: Genome) -> int:
    genome.run_tree()
    agent = genome.bb.get("agent") # agent of THIS behavior tree
    print("cheese eaten: ", agent.cheeseEaten)
    print("time: ", agent.timeStartEnd)
    print(len(genome.pArray))
    value = agent.cheeseEaten + agent.timeStartEnd - (len(genome.pArray) / 1000)
    genome.fitness = value
    print("fitness: ", value)
    time.sleep(2)
    return value # TODO: determine what genome length is too 'long'

    # more cheese eaten -> better
    # longer time alive -> better
    # shorter genome -> better (no need to overcomplicate)

# choose two best from population
def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    the_weights = [fitness_func(genome) for genome in population] # fitness values
    if all(weight == 0 for weight in the_weights):
        # If all weights are zero, assign a default weight
        default_weight = 1
        weights = [default_weight] * len(population)
    return choices(
        population=population,
        weights=the_weights, # fitness values
        k=2
    )

def find_point(tree) -> Tuple[Union[py_trees.composites.Selector, py_trees.composites.Sequence], int]:
    # find a point in the tree to do crossover (must be a selector or sequence)
    # return a reference to the PARENT, and the index of the child whose subtree we move to the other tree
    # if you have children, check each of the children, if one is selector/sequence roll the dice
    def find_subtrees(tree, candidates) -> List[Tuple]:
        if isinstance(tree, (py_trees.composites.Sequence, py_trees.composites.Selector)):
            if tree.children != []:
                for index, node in enumerate(tree.children):
                    if isinstance(node, (py_trees.composites.Sequence, py_trees.composites.Selector)):
                        candidates = find_subtrees(node, candidates + [(tree, index)])
                    

        return candidates # empty list if no children or if root is not sequence/selector(shouldn't be possible)
    # randomly choose subtree
    options = find_subtrees(tree, [])
    print("our options are: ", options)
    if options == []: #CASE: no subtrees
        return tree, -1 
    return random.choice(options)

def canCross(index): # we made index -1 if there is no subtree
    return index != -1

def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    # recursively search behavior tree till find 
    print("BEFORE CROSS")
    display.render_dot_tree(a.tree, name="a_original")
    display.render_dot_tree(b.tree, name="b_original")
    time.sleep(3)
    point1, aIndex = find_point(a.tree)
    point2, bIndex = find_point(b.tree)

    print("A: ", aIndex, " B: ", bIndex)
    if not canCross(aIndex) and not canCross(bIndex): # No subtrees -> NO CHANGE
        print("1 woo")
    elif not canCross(aIndex) and canCross(bIndex):
        # a has no subtrees, b has subtrees
        print("2 woo")
        point2.children[bIndex] = deepcopy(point1) # A
    elif canCross(aIndex) and not canCross(bIndex):
        print("3 woo")
        point1.children[aIndex] = deepcopy(point2)

    else:
        print("FINAL CASE REGULAR CROSS")
        temp = point1.children[aIndex]
        point1.children[aIndex] = point2.children[bIndex] 
        point2.children[bIndex] = temp
    
    display.render_dot_tree(a.tree, name="a_cross")
    display.render_dot_tree(b.tree, name="b_cross")
    print("DONE CORSSING")
    time.sleep(10)
    a.fitness = -1 # tree has been altered so fitness is no longer valid
    b.fitness = -1 # tree has been altered so fitness is no longer valid
    return a, b #hmm maybe a and b aren't the ones changed in rare scenarios

def mutation(tree, num:int = 1, probability:float = 0.5):
    # recursively go through the tree and mutate children with probability
    if tree is None: #base case
        return 
    print("mutate")
    time.sleep(3)
    if isinstance(tree, (py_trees.composites.Sequence, py_trees.composites.Selector)):
        if tree.children != []:
            for index, node in enumerate(tree.children):
                if random.random() < probability: # mutate
                    if isinstance(node, (py_trees.composites.Sequence, py_trees.composites.Selector)):
                        choice = random.choice([0,1]) # 0 or 1
                        children = node.children
                        for child in children: # the children must become orphans before reassigning them
                            child.remove_parent()
                        
                        if choice == 0:
                            tree.children[index] = py_trees.composites.Sequence("Sequence", memory=True, children=children)
                        elif choice == 1:
                            tree.children[index] = py_trees.composites.Selector("Selector", memory=True, children=children)
                        
                        mutation(node, num, probability)

                    elif isinstance(node, Node):
                        type = random.choice(["cheesecond", "firecond", "move"])
                        direction = random.choice(["left", "right", "up", "down"])
                        if type == "move":
                            tree.children[index] = Move(direction, None)
                        elif type == "cheesecond":
                            tree.children[index] = CondCheese(direction, None)
                        elif type == "firecond":   
                            tree.children[index] = CondFire(direction, None)

def run_evolution(
        populate_func: PopulateFunc,
        fitness_func: FitnessFunc,
        fitness_limit: int,
        selection_func: SelectionFunc = selection_pair,
        crossover_func: CrossoverFunc = single_point_crossover,
        mutation_func: MutationFunc = mutation,
        generation_limit: int = 100 # max amount of generations it will doo
    ) -> Tuple[Population, int]:

    # Set a new recursion limit (e.g., 2000)
    sys.setrecursionlimit(2000)

    population = populate_func() # populate

    # run i generations, each time keeping top two, but alsos selecting by weight other genomes
    #doing cross over and mutation on them to create new genomes
    #then once we are done with all generations, we sort the population by fitness
    for i in range(generation_limit):
        print("generation: ", i)
        population = sorted(population, key=lambda genome: fitness_func(genome), reverse=True) # sort by fitness
        
        # check if top genomes have reached limit aka success
        if fitness_func(population[0]) >= fitness_limit:
            break

        next_generation = population[:2] # keep the top two genomes to avoid accidentally destroying them

        # generate next pop. Each loop adds 2, and we already have two so it is length/2 - 1
        print("TIME TO MAKE NEXT GENERATION via mutation and crossover")
        print("looping till j reaches this number", int(len(population)/2) - 1)
        time.sleep(2)
        for j in range(int(len(population)/2) - 1):
            print("INSIDE LOOP")
            time.sleep(1)
            parents = selection_func(population, fitness_func) # two best
            display.render_dot_tree(parents[0].tree, name="parent1")
            display.render_dot_tree(parents[1].tree, name="parent2")
            offspring_a, offspring_b = crossover_func(deepcopy(parents[0]), deepcopy(parents[1])) # deep copy to avoid altering population

            display.render_dot_tree(offspring_a.tree, name="original")
            mutation_func(offspring_a.tree)
            offspring_a.fitness = -1
            display.render_dot_tree(offspring_a.tree, name="mutated")
            mutation_func(offspring_b.tree)
            offspring_b.fitness = -1
            print("DONE MUTATING")
            time.sleep(10)

            next_generation += [offspring_a, offspring_b]

        population = next_generation

    # hmmm goal is to sort the population by its fitness
    # I guess I should run it inside the fitness func
    population = sorted(population, key=lambda genome: fitness_func(genome), reverse=True) # sort by fitness

    return population, i

genome_size = 200
start = time.time()
population,generation = run_evolution(
    populate_func=partial(generate_population, size=5, genome_length=genome_size), #size:int, genome_length: int
    fitness_func=fitness,
    fitness_limit=100,
    generation_limit=15,
)
# generate_population(size:int, genome_length: int)
end = time.time()

print("Generations: ", generation)
print("Time: ", end-start)
#print(f"best solution: {genome_to_things(population[0], moreThings)} ")
