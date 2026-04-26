"""2-Approximation Algorithm for Minimum Vertex Cover."""

from utils import Timer


def approx_vertex_cover(graph, cutoff):
    """2-approximation: repeatedly pick an uncovered edge, add both endpoints.

    Returns:
        cover: set of vertex indices.
        trace: list of (timestamp, cover_size) — single entry for approx.
    """
    timer = Timer(cutoff)

    cover = set()
    edges = [(min(u, v), max(u, v)) for (u, v) in graph.edges]

    for u, v in edges:
        if timer.is_time_up():
            break

        if u not in cover and v not in cover:
            cover.add(u)
            cover.add(v)
    trace = [(timer.elapsed(), len(cover))]
    return cover, trace
