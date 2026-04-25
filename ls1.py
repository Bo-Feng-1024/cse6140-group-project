"""Local Search 1 for Minimum Vertex Cover.
Simulated Annealing:
1. Generate an initial feasible solution via approximation.
2. Perturb: remove a random vertex, repair if needed.
3. Accept improvement always; accept worsening with prob e^(-delta/T).
4. Cool down temperature over time.
5. Track best solution found throughout.
"""

import random
import math
from utils import Timer
from approx import approx_vertex_cover


def is_vertex_cover(graph, cover):
    """Check whether cover is a valid vertex cover."""
    for u, v in graph.edges:
        if u not in cover and v not in cover:
            return False
    return True


def repair(graph, cover):
    """
    Greedy repair: add vertices to cover uncovered edges.
    Always picks the vertex that covers the most uncovered edges.
    Returns a valid vertex cover.
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


def local_search_1(graph, cutoff, seed):
    """
    Simulated Annealing for Minimum Vertex Cover.

    Neighborhood move: remove k random vertices -> repair -> candidate solution.
    Accept if better; accept with probability e^(-delta/T) if worse.

    Returns:
        best_cover : set of vertex indices (minimum found).
        trace      : list of (timestamp, cover_size) recording improvements.
    """
    random.seed(seed)
    timer = Timer(cutoff)

    # Initial solution via approximation
    init_cover, _ = approx_vertex_cover(graph, cutoff)
    current = set(init_cover)
    best_cover = set(current)
    trace = [(timer.elapsed(), len(best_cover))]

    # SA hyperparameters
    T = len(current) * 0.5  # Initial temperature, scaled to solution size
    T_min = 0.01  # Minimum temperature threshold
    alpha = 0.995  # Cooling rate (multiply T by alpha each step)
    steps_per_temp = max(10, graph.n // 10)  # Iterations per temperature level

    # Main loop
    while not timer.is_time_up() and T > T_min:
        for _ in range(steps_per_temp):
            if timer.is_time_up():
                break

            # Generate candidate: remove k vertices then repair
            # High T -> large k (exploration); Low T -> k=1 (exploitation)
            k = max(1, int(T / (len(current) * 0.1 + 1e-9)))
            k = min(k, max(1, len(current) // 4))

            to_remove = random.sample(list(current), k)
            candidate = repair(graph, current - set(to_remove))

            # SA acceptance criterion
            delta = len(candidate) - len(current)

            if delta <= 0:
                # Accept improvements and sideways moves unconditionally
                current = candidate
            elif random.random() < math.exp(-delta / T):
                # Accept worsening move with probability e^(-delta/T)
                current = candidate

            # Update global best
            if len(current) < len(best_cover):
                best_cover = set(current)
                trace.append((timer.elapsed(), len(best_cover)))

        # Cool down
        T *= alpha

    return best_cover, trace
