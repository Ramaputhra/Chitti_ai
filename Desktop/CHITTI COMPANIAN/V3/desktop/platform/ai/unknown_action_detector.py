import logging
from typing import Dict, Any
from desktop.models.semantic_models import DesktopIntent

logger = logging.getLogger(__name__)

class UnknownActionDetector:
    """
    Flags when an Intent cannot be resolved to an existing capability.
    """
    def detect(self, intent: DesktopIntent, resolved_capabilities: list) -> bool:
        if not resolved_capabilities:
            logger.info(f"UnknownActionDetector: Intent '{intent.action.name} {intent.target}' is UNKNOWN.")
            return True
        return False
