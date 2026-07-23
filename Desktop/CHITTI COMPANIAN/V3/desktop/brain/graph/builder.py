import uuid
import time
from desktop.brain.graph.models import GraphNode, GraphDelta

class GraphBuilder:
    def build_delta(self, episode):
        node1 = GraphNode("n_arch", "CONCEPT", "architecture", [episode["episode_id"]])
        return GraphDelta(
            delta_id=str(uuid.uuid4()),
            source_episode_id=episode["episode_id"],
            graph_schema_version="v2.1.0",
            timestamp=time.time(),
            added_nodes=[node1],
            added_edges=[]
        )
