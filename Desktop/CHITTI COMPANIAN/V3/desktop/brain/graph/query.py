class GraphQuery:
    def __init__(self, runtime):
        self.runtime = runtime

    def find_neighborhood(self, node_id: str, depth: int = 1):
        # Stub for topological traversal
        if node_id in self.runtime.nodes:
            return {"nodes": [self.runtime.nodes[node_id]], "edges": []}
        return {"nodes": [], "edges": []}
