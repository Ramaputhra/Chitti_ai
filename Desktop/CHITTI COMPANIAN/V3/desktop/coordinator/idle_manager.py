import logging

logger = logging.getLogger(__name__)

class IdleManager:
    """S36E: Idle Manager overseeing idle state transitions."""
    def trigger_idle(self):
        logger.info("[IdleManager] Visual Coordinator transitioned to Idle mode.")
