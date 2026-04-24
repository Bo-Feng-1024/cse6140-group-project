"""Branch and Bound for Minimum Vertex Cover."""

from utils import Timer


def branch_and_bound(graph, cutoff):
    """Exact Branch-and-Bound algorithm.

    Returns:
        best_cover: set of vertex indices in the optimal cover.
        trace: list of (timestamp, cover_size) recording each improvement.
    """
    timer = Timer(cutoff)
    trace = []

    # TODO: implement Branch-and-Bound
    # Key design decisions:
    #   1. Branching strategy: pick an uncovered edge (u,v), branch on
    #      "include u" vs "include v"
    #   2. Lower bound: e.g. LP relaxation, or maximal matching size
    #   3. Upper bound: initialize with approx algorithm result
    #   4. Pruning: prune when lower_bound >= current best

    best_cover = set(range(1, graph.n + 1))  # trivial: all vertices
    trace.append((timer.elapsed(), len(best_cover)))

    return best_cover, trace
