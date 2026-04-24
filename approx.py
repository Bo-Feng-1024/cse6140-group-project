"""2-Approximation Algorithm for Minimum Vertex Cover."""

from utils import Timer


def approx_vertex_cover(graph, cutoff):
    """2-approximation: repeatedly pick an uncovered edge, add both endpoints.

    Returns:
        cover: set of vertex indices.
        trace: list of (timestamp, cover_size) — single entry for approx.
    """
    timer = Timer(cutoff)

    # TODO: implement the 2-approximation algorithm
    # Algorithm (from lecture):
    #   C = empty set
    #   E' = copy of E
    #   while E' is not empty:
    #       pick any edge (u,v) from E'
    #       add u and v to C
    #       remove all edges incident to u or v from E'
    #   return C

    cover = set()

    trace = [(timer.elapsed(), len(cover))]
    return cover, trace
