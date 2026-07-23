import logging
from typing import Dict, Any
from desktop.platform.components.learned_capability_registry import LearnedCapabilityRegistry

logger = logging.getLogger(__name__)

class CapabilityPromoter:
    """
    Persists a generalized CapabilityCandidate into the LearnedCapabilityRegistry.
    """
    def __init__(self, registry: LearnedCapabilityRegistry):
        self.registry = registry

    def promote(self, intent_signature: str, declarative_graph: Dict[str, Any]) -> str:
        capability_id = f"learned.{intent_signature.replace(' ', '_').lower()}"
        logger.info(f"CapabilityPromoter: Promoting new capability {capability_id}")
        
        self.registry.save_workflow(capability_id, declarative_graph)
        return capability_id
