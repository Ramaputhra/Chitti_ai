from typing import Callable, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CapabilityRegistry:
    """
    Decouples AI Intents (strings) from Python Execution Logic.
    The AI Runtime never knows about Python modules; it just outputs an intent string.
    This registry maps that intent string to a concrete function.
    """
    def __init__(self):
        self._capabilities: Dict[str, Callable] = {}

    def register(self, intent_name: str, executor: Callable) -> None:
        """Register a Python callable to handle a specific intent."""
        self._capabilities[intent_name] = executor
        logger.debug(f"Registered capability: {intent_name} -> {executor.__name__}")

    def execute(self, intent_name: str, **kwargs) -> bool:
        """Find the capability by intent and execute it."""
        executor = self._capabilities.get(intent_name)
        if not executor:
            logger.error(f"No capability registered for intent: {intent_name}")
            return False
            
        try:
            executor(**kwargs)
            logger.info(f"Successfully executed capability: {intent_name}")
            return True
        except Exception as e:
            logger.error(f"Capability execution failed for {intent_name}: {e}")
            return False

# Global instance for the Desktop App (or injected via CompositionRoot)
capability_registry = CapabilityRegistry()
