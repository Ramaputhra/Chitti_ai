import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LearnedCapabilityRegistry:
    """
    Stores declarative workflow graphs (YAML/JSON) learned via ACA.
    CHITTI never generates or stores executable Python code.
    """
    def __init__(self):
        # Maps capability_id (e.g. "learned.compress.pngs") to its YAML/JSON declarative graph
        self.learned_capabilities: Dict[str, Any] = {}

    def save_workflow(self, capability_id: str, declarative_graph: Dict[str, Any]) -> None:
        logger.info(f"LearnedCapabilityRegistry: Saving new declarative workflow {capability_id}")
        self.learned_capabilities[capability_id] = declarative_graph

    def get_workflow(self, capability_id: str) -> Dict[str, Any]:
        return self.learned_capabilities.get(capability_id)
