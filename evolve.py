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
import os
import shutil
import threading
import concurrent.futures
import math

GENERATION_SIZE = 10
Population = List[Genome]
FitnessFunc = Callable[[Genome], int] # how good genome is
PopulateFunc = Callable[[], Population]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]

def delete_files_starting_with(prefix):
    # Get the current working directory
    cwd = os.getcwd()
    # List all files in the directory
    files = os.listdir(cwd)
    # Iterate over the files
    for file in files:
        # Check if the file starts with the specified prefix
        if file.startswith(prefix):
            file_path = os.path.join(cwd, file)
            delete_file(file_path)

def delete_files_ending_with(suffix):
    cwd = os.getcwd()
    files = os.listdir(cwd)
    for file in files:
        if file.endswith(suffix):
            file_path = os.path.join(cwd, file)
            os.remove(file_path)

def delete_file(filename):
    try:
        os.remove(filename)
        print(f"File '{filename}' deleted successfully.")
    except OSError as e: # Handle the case where the file doesn't exist or there's a permission error
        print(f"Error deleting file '{filename}': {e}")

def generate_genome(length: int) -> Genome:
    numbers = [random.randint(0,9) for _ in range(length)] # length of circular array
    array = CircularArray(numbers)
    return Genome(array)

def generate_population(size:int, genome_length: int)-> Population: # originally al the same length before made into trees
    return [generate_genome(genome_length) for _ in range(size)] # list of lists

def fitness(genome: Genome) -> int:
    # more cheese eaten, more time alive, shorter genome -> better
    if genome.fitness != -1: # if fitness is already calculated
        return genome.fitness
    try:
        genome.run_tree()
        assert genome.bb is not None
        agent = genome.bb.get("agent")
        # .05 because staying alive counts for something
        #value = (.05 + agent.cheeseEaten/agent.totalCheese) * (agent.steps + agent.trialTime - (len(genome.pArray) / 1000))
        value = (agent.cheeseEaten*10) + (2 * math.log(len(genome.pArray)+.0001))
        if len(genome.pArray) > 150: # penalize for being too long
            value *= .5
        
        genome.fitness = value
        print("cheese eaten:", agent.cheeseEaten, "time:", agent.trialTime, "steps:", agent.steps, "parray:", len(genome.pArray))
        print("fitness: ", value)
        return value # used sometimes, but not always
    except RecursionError:
        print("running tree: oh no we have a recursion error")
        genome.fitness = 0 # get removed from the population
        return genome.fitness
# choose two best from population 
def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    population = population[:] # working with a copy just in case
    one = choices(
        population=population,
        weights=[genome.fitness for genome in population] , # fitness values
    )[0]
    population.remove(one)
    two = choices(
        population=population,
        weights=[genome.fitness for genome in population] , # fitness values
    )[0]
    assert one != two

    return one, two


def prune(a: Genome) -> Genome: # this function will actually alter...no you need to alter genome though
    array = a.pArray[:]
    # locate parent w one child, pop parent from array
    a.tree.root = True
    def p(tree):
        if isinstance(tree, (py_trees.composites.Sequence, py_trees.composites.Selector)):
            print(tree.children)
            if len(tree.children) == 1 and (tree.root == False or isinstance(tree.children[0], (py_trees.composites.Sequence, py_trees.composites.Selector))): # we cannot remove root
                p(tree.children[0])
                print("deleting from index", tree.index, "to but not including", tree.children[0].index)
                del array[tree.index:tree.children[0].index]
            else:
                # is either the root (can't remove itself) or has more than one child
                for child in tree.children:
                    p(child)
    p(a.tree)
    if(array == a.pArray):
        return a
    return Genome(CircularArray(array))
    # locate a parent with only one child, replace parent with child

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
    if options == []: #CASE: no subtrees
        return tree, -1 
    return random.choice(options)

def find_end_index(tree):
    # given a tree, find the index stored within the last node
    if isinstance(tree, (py_trees.composites.Sequence, py_trees.composites.Selector)):
        if tree.children != []:
            return find_end_index(tree.children[-1])
    elif isinstance(tree, Node):
        # a terminal
        return tree.index

def canCross(index): # we made index -1 if there is no subtree
    return index != -1

def genome_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    # crosses over two genomes by editing their genome sequence only
    point1, aIndex = find_point(a.tree)
    point2, bIndex = find_point(b.tree)

    if not canCross(aIndex) and not canCross(bIndex): # No subtrees -> NO CHANGE
        return a,b # no change so no need to create new genomes
    elif not canCross(aIndex) and canCross(bIndex):
        # b has subtrees, a doesn't
        # a is put into b so create new genome for b
        sectionForB = a.pArray[:]
        bStartIndex = point2.children[bIndex].index
        bEndIndex = find_end_index(point2.children[bIndex])

        if len(b.pArray) == bEndIndex + 1:
            newB = b.pArray[:bStartIndex] + sectionForB
        else:
            newB = b.pArray[:bStartIndex] + sectionForB + b.pArray[bEndIndex+1:]

        return a, Genome(CircularArray(newB))

    elif canCross(aIndex) and not canCross(bIndex):
        # a has subtrees, b doesn't -> b is put into a
        sectionForA = b.pArray[:]
        aStartIndex = point1.children[aIndex].index
        aEndIndex = find_end_index(point1.children[aIndex])

        if len(a.pArray) == aEndIndex + 1:
            newA = a.pArray[:aStartIndex] + sectionForA
        else:
            newA = a.pArray[:aStartIndex] + sectionForA + a.pArray[aEndIndex+1:]

        return Genome(CircularArray(newA)), b

    else:
        aStartIndex = point1.children[aIndex].index
        bStartIndex = point2.children[bIndex].index

        aEndIndex = find_end_index(point1.children[aIndex])
        bEndIndex = find_end_index(point2.children[bIndex])

        sectionForB = a.pArray[aStartIndex:aEndIndex]
        sectionForA = b.pArray[bStartIndex:bEndIndex] # represents a subtree

        if len(b.pArray) == bEndIndex + 1:
            newB = b.pArray[:bStartIndex] + sectionForB
        else:
            newB = b.pArray[:bStartIndex] + sectionForB + b.pArray[bEndIndex+1:]

        if len(a.pArray) == aEndIndex + 1:
            newA = a.pArray[:aStartIndex] + sectionForA
        else:
            newA = a.pArray[:aStartIndex] + sectionForA + a.pArray[aEndIndex+1:]

        return Genome(CircularArray(newA)), Genome(CircularArray(newB))
    
def genome_mutate(a: Genome, num=1, probability=.5) -> Genome:
    print("mutate")
    array = a.pArray[:]
    # sequence / selector take 1 number, move and cond take 2
    def mutate(tree):
        if random.random() < probability:
            if isinstance(tree, (py_trees.composites.Sequence, py_trees.composites.Selector)):
                array[tree.index] = random.randint(0,9)
            elif isinstance(tree, Node):
                array[tree.index] = random.randint(0,9)
                array[tree.index+1] = random.randint(0,9)
        elif isinstance(tree, (py_trees.composites.Sequence, py_trees.composites.Selector)):
            for child in tree.children:
                mutate(child)
    mutate(a.tree)
    return Genome(CircularArray(array))

def write_fitness_to_file(population):
    with open("fitness_values.txt", "a") as f:
        for genome in population:
            f.write(str(round(genome.fitness, 4)) + ", ")
        f.write("\n")

def write_genomes_to_file(population):
    with open("genomes.txt", "a") as f:
        result = ""
        for i in range(3):
            result += "".join(str(item) for item in population[i].pArray) 
            result+= ","
        f.write(result + "\n")

def clear_folder(name):
    try:
        # Iterate over all files and subdirectories in the directory
        for item in os.listdir(name):
            item_path = os.path.join(name, item)
            if os.path.isfile(item_path):
                os.remove(item_path)  # Remove file
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove directory and its contents recursively
        
        print(f"Folder '{name}' successfully cleared.")
    except OSError as e:
        print(f"Error: {e.strerror}")

def run_evolution(
        populate_func: PopulateFunc,
        fitness_func: FitnessFunc,
        fitness_limit: int,
        selection_func: SelectionFunc = selection_pair,
        crossover_func: CrossoverFunc = genome_crossover,
        mutation_func: MutationFunc = genome_mutate,
        generation_limit: int = 100 # max amount of generations it will doo
    ) -> Tuple[Population, int]:

    # Set a new recursion limit (e.g., 2000)
    sys.setrecursionlimit(2000)
    delete_file("fitness_values.txt")
    delete_file("genomes.txt")
    delete_files_starting_with("best")
    clear_folder("results")

    population = populate_func() # populate
    for i in range(generation_limit): # loop represents the creation of a new generation
        print("generation: ", i)
        MAX_THREADS = GENERATION_SIZE
        # Create a ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = [] # Create a list to store the futures
            for genome in population:
                if genome.fitness == -1: # if fitness is not already calculated
                    # Submit the task to the executor
                    future = executor.submit(fitness_func, genome)
                    futures.append(future) # Append the future object to the list
            # Wait for all tasks to complete
            concurrent.futures.wait(futures)

        # fitness should be all be set now
        population = sorted(population, key=lambda genome: genome.fitness, reverse=True) # sort by fitness
        write_fitness_to_file(population)
        

        population = [item for item in population if item.fitness != 0] # remove the trees that have recursion errors (too big)
        write_genomes_to_file(population)
        # check if top genomes have reached limit aka success
        if fitness_func(population[0]) >= fitness_limit:
            break

        next_generation = population[:2] # keep the top two genomes to avoid accidentally destroying them

        if i % 20 == 0:
            next_generation = [prune(pop) for pop in next_generation]
            next_generation[0].build_tree()
            next_generation[1].build_tree()

            name = "best_one_generation_" + str(i)
            display.render_dot_tree(next_generation[0].tree, name=name)
            new_path = os.path.join("results", name + ".png")
            os.rename(name + ".png", new_path)

            name = "2nd_best_one_generation_" + str(i)
            display.render_dot_tree(next_generation[1].tree, name=name)
            new_path = os.path.join("results", name + ".png")
            os.rename(name + ".png", new_path)

            name = "3rd_best_one_generation_" + str(i)
            display.render_dot_tree(population[2].tree, name=name)
            new_path = os.path.join("results", name + ".png")
            os.rename(name + ".png", new_path)

            delete_files_ending_with(".dot")
            delete_files_ending_with(".svg")

        # generate next pop. Each loop adds 2, and we already have two so it is length/2 - 1
        print("TIME TO MAKE NEXT GENERATION via mutation and crossover")
        j = 0
        while j < int(GENERATION_SIZE/2) - 1:
            print("INSIDE LOOP", j)
            j+=1
            parents = selection_func(population, fitness_func) # two best
            offspring_a, offspring_b = crossover_func(parents[0], parents[1])
            
            try:
                if offspring_a.fitness == -1:
                    offspring_a.build_tree() 
                if offspring_b.fitness == -1:
                    offspring_b.build_tree()
            except RecursionError:
                print("build: oh no we have a recursion error")
                # lets try again
                j -= 1
                continue

            offspring_a = mutation_func(offspring_a)
            offspring_b = mutation_func(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation
    population = sorted(population, key=lambda genome: genome.fitness, reverse=True) # sort by fitness

    return population, i

genome_size = 200
start = time.time()
# population,generation = run_evolution(
#     populate_func=partial(generate_population, size=GENERATION_SIZE, genome_length=genome_size), #size:int, genome_length: int
#     fitness_func=fitness,
#     fitness_limit=1000000,
#     generation_limit=1000,
# )
# # generate_population(size:int, genome_length: int)
# end = time.time()

# print("Generations: ", generation)
# print("Time: ", end-start)
