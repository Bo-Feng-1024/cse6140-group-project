"""Local Search 2 for Minimum Vertex Cover.

TODO: Decide algorithm variant in group meeting.
Must differ from LS1 by family, neighborhood, or perturbation strategy.
"""

import random
from utils import Timer


def local_search_2(graph, cutoff, seed):
    """Local Search variant 2.

    Returns:
        best_cover: set of vertex indices.
        trace: list of (timestamp, cover_size) recording improvements.
    """
    random.seed(seed)
    timer = Timer(cutoff)
    trace = []

    # TODO: implement Local Search 2
    # Must differ from LS1 in at least one of:
    #   - Algorithm family (e.g., SA vs GA vs HC)
    #   - Neighborhood definition
    #   - Perturbation strategy

    best_cover = set(range(1, graph.n + 1))  # placeholder
    trace.append((timer.elapsed(), len(best_cover)))

    return best_cover, trace
