from typing import List, Tuple
from random import choices, randint, randrange, random
from collections import namedtuple
from typing import List, Callable
from functools import partial
import time

Genome = List[int]
Population = List[Genome]
FitnessFunc = Callable[[Genome], int] # how good genome is
PopulateFunc = Callable[[], Population]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]


Thing = namedtuple('Thing', ['name', 'value', 'weight'])


things = [
    Thing('Laptop', 500, 2200),
    Thing('Headphones', 150, 160),
    Thing('Coffee Mug', 60, 350),
    Thing('Notepad', 40, 333),
    Thing('Water Bottle', 30, 192),
]

moreThings = [ 
    Thing('Mints', 5, 25),
    Thing('Socks', 10, 38),
    Thing('Tissues', 15, 80),
    Thing('Phone', 500, 200),
    Thing('Baseball Cap', 100, 70),
]

def generate_genome(length: int) -> Genome:
    return choices([0, 1], k=length)

def generate_population(size:int, genome_length: int)-> Population:
    return [generate_genome(genome_length) for _ in range(size)]

def fitness(genome: Genome, things: [Thing], weight_limit: int) -> int:
    if len(genome) != len(things):
        raise ValueError("genome and things must be of the same length")

    weight = 0
    value = 0

    for i, thing in enumerate(things):
        if genome[i] == 1:
            weight += thing.weight
            value += thing.value

        if weight > weight_limit:
            return 0
        
    return value


# higher weights are more likely to be chosen that is
def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    return choices(
        population=population,
        weights=[fitness_func(genome) for genome in population],
        k=2
    )

# crossover two genomes to produce two children
def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    if len(a) != len(b):
        raise ValueError("Genomes a and b must be of same length")
    
    p = randint(1,len(a)-1) # index to combine them at

    return a[:p] + b[p:], b[:p] + a[p:]

def mutation(genome: Genome, num:int = 1, probability:float = 0.5) -> Genome:
    # flip num bits with probability
    for _ in range(num):
        index = randrange(len(genome)) # pick random index
        genome[index] = genome[index] if random() > probability else abs(genome[index]-1)  # flip bit
    return genome



def run_evolution(
        populate_func: PopulateFunc,
        fitness_func: FitnessFunc,
        fitness_limit: int,
        selection_func: SelectionFunc = selection_pair,
        crossover_func: CrossoverFunc = single_point_crossover,
        mutation_func: MutationFunc = mutation,
        generation_limit: int = 100 # max amount of generations it will doo
    ) -> Tuple[Population, int]:

    population = populate_func() # populate

    # run i generations, each time keeping top two, but alsos selecting by weight other genomes
    #doing cross over and mutation on them to create new genomes
    #then once we are done with all generations, we sort the population by fitness
    for i in range(generation_limit):
        population = sorted(population, key=lambda genome: fitness_func(genome), reverse=True) # sort by fitness
        
        # check if top genomes have reached limit aka success
        if fitness_func(population[0]) >= fitness_limit:
            break

        next_generation = population[:2] # keep the top two genomes to avoid accidentally destroying them

        # generate next pop. Each loop adds 2, and we already have two so it is length/2 - 1
        for j in range(int(len(population)/2) - 1):
            parents = selection_func(population, fitness_func)
            offspring_a, offspring_b = crossover_func(parents[0], parents[1])

            offspring_a = mutation_func(offspring_a)
            offspring_b = mutation_func(offspring_b)

            next_generation += [mutation_func(offspring_a), mutation_func(offspring_b)]

        population = next_generation


    population = sorted(population, key=lambda genome: fitness_func(genome), reverse=True) # sort by fitness

    return population, i

start = time.time()
population,generation = run_evolution(
    populate_func=partial(generate_population, size=10, genome_length=len(things)),
    fitness_func=partial(fitness, things=things, weight_limit=3000),
    fitness_limit=740,
    generation_limit=100,
)
end = time.time()


def genome_to_things(genome: Genome, things: [Thing]) -> [Thing]:
    result = []
    for i, thing in enumerate(things):
        if genome[i] == 1:
            result += [thing.name]
    return result

print("Generations: ", generation)
print("Time: ", end-start)
print(f"best solution: {genome_to_things(population[0], moreThings)} ")
