from desktop.brain.graph.models import GraphDelta, GraphEdge

class GraphRuntime:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.schema_version = "v2.1.0"
        
    def apply_delta(self, delta: GraphDelta):
        for node in delta.added_nodes:
            if node.node_id not in self.nodes:
                self.nodes[node.node_id] = node
            else:
                self.nodes[node.node_id].source_episode_ids.extend(node.source_episode_ids)
                
        for edge in delta.added_edges:
            if edge.edge_id not in self.edges:
                self.edges[edge.edge_id] = edge
            else:
                existing = self.edges[edge.edge_id]
                new_conf = max(existing.confidence, edge.confidence)
                existing.source_episode_ids.extend(edge.source_episode_ids)
                self.edges[edge.edge_id] = GraphEdge(
                    edge_id=edge.edge_id, source_node_id=edge.source_node_id, 
                    target_node_id=edge.target_node_id, relationship_type=edge.relationship_type, 
                    source_episode_ids=list(set(existing.source_episode_ids)), confidence=new_conf)
