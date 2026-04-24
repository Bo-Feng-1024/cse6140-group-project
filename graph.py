"""Graph data structure and I/O for Minimum Vertex Cover."""

class Graph:
    def __init__(self, n, edges):
        self.n = n                      # number of vertices (1-indexed)
        self.edges = edges              # list of (u, v) tuples
        self.m = len(edges)
        # adjacency list: adj[v] = set of neighbors
        self.adj = [set() for _ in range(n + 1)]
        for u, v in edges:
            self.adj[u].add(v)
            self.adj[v].add(u)

    def degree(self, v):
        return len(self.adj[v])

    def max_degree_vertex(self):
        """Return the vertex with the highest degree among vertices 1..n."""
        best_v, best_d = 1, self.degree(1)
        for v in range(2, self.n + 1):
            d = self.degree(v)
            if d > best_d:
                best_v, best_d = v, d
        return best_v


def read_graph(filepath):
    """Read a graph from <filepath>.in and return a Graph object."""
    if not filepath.endswith('.in'):
        filepath = filepath + '.in'
    with open(filepath, 'r') as f:
        first_line = f.readline().split()
        n, m = int(first_line[0]), int(first_line[1])
        edges = []
        for _ in range(m):
            parts = f.readline().split()
            u, v = int(parts[0]), int(parts[1])
            edges.append((u, v))
    return Graph(n, edges)


def is_vertex_cover(graph, cover):
    """Check whether `cover` (a set of vertex indices) covers all edges."""
    for u, v in graph.edges:
        if u not in cover and v not in cover:
            return False
    return True
