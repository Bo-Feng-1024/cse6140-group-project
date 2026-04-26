"""Branch and Bound for Minimum Vertex Cover.

Search strategy: vertex-branching DFS with bounding.
    Pick a vertex v of maximum residual degree.
    Branch 1: v in cover.
    Branch 2: v not in cover -- then every neighbor of v must be in cover,
              so include all of N(v) at once.

Initial upper bound: 2-approximation cover (approx_vertex_cover).

Lower bound at each node: size of a greedy maximal matching on the
residual subgraph. Any vertex cover must include at least one endpoint
of every matched edge, so |VC*| >= |maximal matching|.

Per-node reductions (applied repeatedly until no longer applicable):
    - Isolated vertex: drop from residual.
    - Degree-1 vertex v with sole neighbor u: force u into cover, drop both.
"""

import sys

from utils import Timer
from approx import approx_vertex_cover


def _maximal_matching_size(active, adj):
    """Greedy maximal matching size on the subgraph induced by active vertices."""
    matched = set()
    size = 0
    for u in active:
        if u in matched:
            continue
        for w in adj[u]:
            if w in active and w not in matched:
                matched.add(u)
                matched.add(w)
                size += 1
                break
    return size


def _pick_branching_vertex(active, adj):
    """Return (v, deg) with v of maximum residual degree; (-1, 0) if no active edges remain."""
    best_v, best_d = -1, 0
    for v in active:
        d = 0
        for w in adj[v]:
            if w in active:
                d += 1
        if d > best_d:
            best_v, best_d = v, d
    return best_v, best_d


def branch_and_bound(graph, cutoff):
    """Exact Branch-and-Bound for Minimum Vertex Cover.

    Args:
        graph: Graph object (1-indexed adjacency list).
        cutoff: wall-clock time limit in seconds.

    Returns:
        best_cover: set of vertex indices (best cover found within cutoff).
        trace: list of (timestamp, cover_size) recording each improvement.
    """
    sys.setrecursionlimit(50000)
    timer = Timer(cutoff)
    n, adj = graph.n, graph.adj

    init_cover, _ = approx_vertex_cover(graph, cutoff)
    state = {
        'best': set(init_cover),
        'trace': [(timer.elapsed(), len(init_cover))],
    }

    active = {v for v in range(1, n + 1) if adj[v]}
    cover = set()

    def update_best():
        if len(cover) < len(state['best']):
            state['best'] = set(cover)
            state['trace'].append((timer.elapsed(), len(cover)))

    def search():
        if timer.is_time_up():
            return

        # Reductions: iterate until no degree-0/degree-1 vertex remains.
        undo = []
        queue = list(active)
        while queue:
            v = queue.pop()
            if v not in active:
                continue
            nbrs_active = [w for w in adj[v] if w in active]
            if not nbrs_active:
                active.discard(v)
                undo.append(('a', v))
            elif len(nbrs_active) == 1:
                u = nbrs_active[0]
                cover.add(u)
                undo.append(('c', u))
                active.discard(u)
                undo.append(('a', u))
                active.discard(v)
                undo.append(('a', v))
                for w in adj[u]:
                    if w in active:
                        queue.append(w)

        try:
            if len(cover) >= len(state['best']):
                return

            lb = _maximal_matching_size(active, adj)
            if len(cover) + lb >= len(state['best']):
                return

            v, dv = _pick_branching_vertex(active, adj)
            if v == -1:
                update_best()
                return

            cover.add(v)
            active.discard(v)
            search()
            cover.discard(v)
            active.add(v)

            if timer.is_time_up():
                return

            nbrs = [w for w in adj[v] if w in active]
            for w in nbrs:
                cover.add(w)
                active.discard(w)
            search()
            for w in nbrs:
                cover.discard(w)
                active.add(w)
        finally:
            while undo:
                op, x = undo.pop()
                if op == 'a':
                    active.add(x)
                else:
                    cover.discard(x)

    search()
    return state['best'], state['trace']
