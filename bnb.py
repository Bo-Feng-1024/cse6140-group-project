"""Branch and Bound for Minimum Vertex Cover.

Pipeline at the root:
    1. Initial upper bound: min of two heuristics --
       (a) the matching-based 2-approximation (approx_vertex_cover);
       (b) a max-residual-degree greedy cover. The greedy is tight on
           dense (e.g. dense bipartite) instances where the
           matching-based 2-approx is loose by a factor close to 2.
    2. Nemhauser-Trotter LP kernelization. Solve the LP relaxation
       of MVC in polynomial time via Hopcroft-Karp on the bipartite
       double cover, then recover the half-integral LP solution by
       Konig's theorem. Vertices with x*_v = 1 are forced into the
       cover, vertices with x*_v = 0 are dropped, and only the
       x*_v = 1/2 set ("kernel") needs to be searched.

In-search at every node:
    3. Reductions (applied to a fixed point):
        - degree-0: drop.
        - degree-1 with neighbor u: force u into cover, drop both.
        - degree-2 with adjacent neighbors (triangle): force both
          neighbors into cover, drop v.
    4. Bound: |C| + |maximal matching on residual| >= |C*| -> prune.
    5. Branch on a vertex v of maximum residual degree:
        Branch 1: v in cover.
        Branch 2: v not in cover -> all of N(v) in cover.

References:
    Nemhauser, Trotter (1975), Math. Programming 8.
    Hochbaum (1982), Discrete Applied Math 6.
    Hopcroft, Karp (1973), SIAM J. Computing 2.
    Niedermeier (2006), Invitation to FPT Algorithms.
"""

import heapq
import sys
from collections import deque

from utils import Timer
from approx import approx_vertex_cover


# ============== Hopcroft-Karp & Nemhauser-Trotter kernel ==============

def _hopcroft_karp(adj_left, n_left, n_right):
    """Maximum bipartite matching. Returns (pair_l, pair_r)."""
    INF = float('inf')
    pair_l = [-1] * n_left
    pair_r = [-1] * n_right
    dist = [0] * n_left

    def bfs():
        q = deque()
        for u in range(n_left):
            if pair_l[u] == -1:
                dist[u] = 0
                q.append(u)
            else:
                dist[u] = INF
        found = False
        while q:
            u = q.popleft()
            for v in adj_left[u]:
                pu = pair_r[v]
                if pu == -1:
                    found = True
                elif dist[pu] == INF:
                    dist[pu] = dist[u] + 1
                    q.append(pu)
        return found

    def dfs(u):
        for v in adj_left[u]:
            pu = pair_r[v]
            if pu == -1 or (dist[pu] == dist[u] + 1 and dfs(pu)):
                pair_l[u] = v
                pair_r[v] = u
                return True
        dist[u] = INF
        return False

    while bfs():
        for u in range(n_left):
            if pair_l[u] == -1:
                dfs(u)
    return pair_l, pair_r


def _nt_kernel(graph):
    """Nemhauser-Trotter half-integral LP kernel via bipartite double cover.

    Returns (v1, v0, v_half) partitioning the non-isolated vertices:
        v1     : LP x*_v = 1, forced into some optimal cover.
        v0     : LP x*_v = 0, excluded from some optimal cover.
        v_half : LP x*_v = 1/2, the residual kernel.
    """
    n, adj = graph.n, graph.adj
    active = [v for v in range(1, n + 1) if adj[v]]
    if not active:
        return set(), set(), set()
    idx = {v: i for i, v in enumerate(active)}
    k = len(active)
    adj_left = [[] for _ in range(k)]
    for u in active:
        i = idx[u]
        for v in adj[u]:
            if v in idx:
                adj_left[i].append(idx[v])

    pair_l, pair_r = _hopcroft_karp(adj_left, k, k)

    # Konig: BFS from unmatched left vertices via alternating paths.
    visited_l, visited_r = set(), set()
    q = deque()
    for u in range(k):
        if pair_l[u] == -1:
            visited_l.add(u)
            q.append(u)
    while q:
        u = q.popleft()
        for v in adj_left[u]:
            if pair_l[u] == v or v in visited_r:
                continue
            visited_r.add(v)
            mate = pair_r[v]
            if mate != -1 and mate not in visited_l:
                visited_l.add(mate)
                q.append(mate)

    v1, v0, v_half = set(), set(), set()
    for v in active:
        i = idx[v]
        in_left = i not in visited_l   # left part of min VC of B
        in_right = i in visited_r      # right part of min VC of B
        if in_left and in_right:
            v1.add(v)
        elif (not in_left) and (not in_right):
            v0.add(v)
        else:
            v_half.add(v)
    return v1, v0, v_half


def _greedy_max_degree_cover(graph):
    """Greedy heuristic UB: repeatedly pick max-residual-degree vertex.

    Often much tighter than the matching-based 2-approx on dense graphs.
    Runs in O((n + m) log n) using a lazy-decrease max-heap.
    """
    n, adj = graph.n, graph.adj
    deg = [len(adj[v]) for v in range(n + 1)]
    heap = [(-deg[v], v) for v in range(1, n + 1) if deg[v] > 0]
    heapq.heapify(heap)
    in_cover = [False] * (n + 1)
    while heap:
        d_neg, v = heapq.heappop(heap)
        if in_cover[v] or -d_neg != deg[v]:
            continue
        if deg[v] == 0:
            break
        in_cover[v] = True
        for w in adj[v]:
            if not in_cover[w] and deg[w] > 0:
                deg[w] -= 1
                if deg[w] > 0:
                    heapq.heappush(heap, (-deg[w], w))
        deg[v] = 0
    return {v for v in range(1, n + 1) if in_cover[v]}


# ============== Search helpers ==============

def _maximal_matching_size(active, adj):
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
    best_v, best_d = -1, 0
    for v in active:
        d = 0
        for w in adj[v]:
            if w in active:
                d += 1
        if d > best_d:
            best_v, best_d = v, d
    return best_v, best_d


# ============== Public entry point ==============

def branch_and_bound(graph, cutoff):
    """Exact Branch-and-Bound for Minimum Vertex Cover.

    Returns (best_cover, trace) where trace = [(timestamp, size), ...].
    """
    sys.setrecursionlimit(50000)
    timer = Timer(cutoff)
    n, adj = graph.n, graph.adj

    init_approx, _ = approx_vertex_cover(graph, cutoff)
    init_greedy = _greedy_max_degree_cover(graph)
    init_cover = init_greedy if len(init_greedy) < len(init_approx) else init_approx

    state = {
        'best': set(init_cover),
        'trace': [(timer.elapsed(), len(init_cover))],
    }

    def maybe_update_best(candidate):
        if len(candidate) < len(state['best']):
            state['best'] = set(candidate)
            state['trace'].append((timer.elapsed(), len(candidate)))

    if timer.is_time_up():
        return state['best'], state['trace']

    v1, v0, v_half = _nt_kernel(graph)
    if not v_half:
        maybe_update_best(v1)
        return state['best'], state['trace']

    active = set(v_half)
    cover = set(v1)
    if len(cover) >= len(state['best']):
        return state['best'], state['trace']

    def search():
        if timer.is_time_up():
            return

        undo = []
        queue = list(active)
        while queue:
            v = queue.pop()
            if v not in active:
                continue
            nbrs_active = [w for w in adj[v] if w in active]
            d = len(nbrs_active)
            if d == 0:
                active.discard(v)
                undo.append(('a', v))
            elif d == 1:
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
            elif d == 2:
                u, w = nbrs_active[0], nbrs_active[1]
                if w in adj[u]:
                    # Triangle case: force both neighbors into cover, drop v.
                    cover.add(u); undo.append(('c', u))
                    cover.add(w); undo.append(('c', w))
                    active.discard(u); undo.append(('a', u))
                    active.discard(w); undo.append(('a', w))
                    active.discard(v); undo.append(('a', v))
                    for x in adj[u]:
                        if x in active:
                            queue.append(x)
                    for x in adj[w]:
                        if x in active:
                            queue.append(x)

        try:
            if len(cover) >= len(state['best']):
                return

            lb = _maximal_matching_size(active, adj)
            if len(cover) + lb >= len(state['best']):
                return

            v, dv = _pick_branching_vertex(active, adj)
            if v == -1:
                maybe_update_best(cover)
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
