"""Local Search 2 for Minimum Vertex Cover.

Genetic Algorithm:
1. Initialize a population with a mix of an approximated cover and randomized greedy covers.
2. Select parents via tournament selection.
3. Crossover via intersection of parent sets.
4. Mutate by dropping random vertices.
5. Repair offspring to ensure validity using a randomized greedy approach.
6. Replace the population while keeping the elite covers.
7. Track the best solution found throughout.
"""

import random
from utils import Timer
from approx import approx_vertex_cover


def repair_randomized(graph, cover):
    """
    Greedy repair with random tie-breaking.
    Adds vertices to cover uncovered edges to guarantee a valid vertex cover.
    """
    new_cover = set(cover)

    uncovered = [
        (u, v) for u, v in graph.edges if u not in new_cover and v not in new_cover
    ]

    while uncovered:
        freq = {}
        for u, v in uncovered:
            freq[u] = freq.get(u, 0) + 1
            freq[v] = freq.get(v, 0) + 1

        max_freq = max(freq.values())
        candidates = [node for node, f in freq.items() if f == max_freq]
        best = random.choice(candidates)

        new_cover.add(best)
        uncovered = [(u, v) for u, v in uncovered if u != best and v != best]

    return new_cover


def local_search_2(graph, cutoff, seed):
    """Local Search variant 2.

    Returns:
        best_cover: set of vertex indices.
        trace: list of (timestamp, cover_size) recording improvements.
    """
    random.seed(seed)
    timer = Timer(cutoff)
    trace = []

    pop_size = max(10, min(40, graph.n // 2))
    mutation_rate = 0.1
    elite_size = max(1, pop_size // 10)
    tournament_size = 3

    population = []
    
    init_cover, _ = approx_vertex_cover(graph, cutoff)
    population.append(set(init_cover))
    
    best_cover = set(init_cover)
    trace.append((timer.elapsed(), len(best_cover)))

    for _ in range(pop_size - 1):
        if timer.is_time_up():
            break
        random_cover = repair_randomized(graph, set())
        population.append(random_cover)
        
        if len(random_cover) < len(best_cover):
            best_cover = set(random_cover)
            trace.append((timer.elapsed(), len(best_cover)))

    while not timer.is_time_up():
        population.sort(key=len)
        new_population = population[:elite_size]

        while len(new_population) < pop_size:
            if timer.is_time_up():
                break
            
            p1 = min(random.sample(population, tournament_size), key=len)
            p2 = min(random.sample(population, tournament_size), key=len)
            
            child = p1.intersection(p2)
            
            if child:
                num_to_remove = int(len(child) * mutation_rate)
                to_remove = set(random.sample(list(child), num_to_remove))
                child = child - to_remove
            
            child = repair_randomized(graph, child)
            
            new_population.append(child)
            
            if len(child) < len(best_cover):
                best_cover = set(child)
                trace.append((timer.elapsed(), len(best_cover)))

        population = new_population

    return best_cover, trace