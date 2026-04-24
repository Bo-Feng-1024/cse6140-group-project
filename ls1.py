"""Local Search 1 for Minimum Vertex Cover.

TODO: Decide algorithm variant in group meeting.
Candidates: Simulated Annealing, Hill Climbing, Genetic Algorithm, etc.
"""

import random
from utils import Timer


def local_search_1(graph, cutoff, seed):
    """Local Search variant 1.

    Returns:
        best_cover: set of vertex indices.
        trace: list of (timestamp, cover_size) recording improvements.
    """
    random.seed(seed)
    timer = Timer(cutoff)
    trace = []

    # TODO: implement Local Search 1
    # Outline:
    #   1. Generate initial solution (e.g., via approx algorithm)
    #   2. Define neighborhood (e.g., swap a vertex in/out of cover)
    #   3. Acceptance criterion (depends on chosen method)
    #   4. Iterate until cutoff

    best_cover = set(range(1, graph.n + 1))  # placeholder
    trace.append((timer.elapsed(), len(best_cover)))

    return best_cover, trace
