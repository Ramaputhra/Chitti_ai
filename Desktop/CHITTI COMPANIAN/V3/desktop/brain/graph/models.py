from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: str
    canonical_name: str
    source_episode_ids: List[str]

@dataclass(frozen=True)
class GraphEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    source_episode_ids: List[str]
    confidence: float

@dataclass(frozen=True)
class GraphDelta:
    delta_id: str
    source_episode_id: str
    graph_schema_version: str
    timestamp: float
    added_nodes: List[GraphNode]
    added_edges: List[GraphEdge]
