import logging
from typing import Dict, Any, List, Optional
import time

from desktop.models.lifecycle import IRuntime, HealthState
from desktop.app.context import KernelContext
from desktop.models.notification import Notification, NotificationPriority, NotificationSource

logger = logging.getLogger(__name__)

class NotificationRuntime(IRuntime):
    """
    Sprint 7.5: Notification Runtime.
    Manages notifications from system, email, and calendar.
    Experiences (like Morning Briefing) consume this instead of querying sources directly.
    """
    def __init__(self):
        self.context: Optional[KernelContext] = None
        self._running = False
        self._notifications: Dict[str, Notification] = {}

    @property
    def dependencies(self) -> List[Any]:
        return []

    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        return True

    async def start(self) -> bool:
        self._running = True
        logger.info("NotificationRuntime started.")
        return True

    async def stop(self) -> bool:
        self._running = False
        return True

    def health(self) -> HealthState:
        return HealthState.HEALTHY

    async def shutdown(self) -> bool:
        return True

    def push_notification(self, notification: Notification):
        """
        Receives a new notification. Handles deduplication.
        """
        if not self._running:
            return
            
        # Basic deduplication by title/body within recent window
        for existing in self._notifications.values():
            if not existing.read and existing.title == notification.title and existing.body == notification.body:
                # Deduplicate if within 1 hour
                if time.time() - existing.received_at < 3600:
                    logger.debug(f"Deduplicated notification: {notification.title}")
                    return
                    
        self._notifications[notification.id] = notification
        logger.info(f"Received Notification: {notification.title}")

    def get_unread_notifications(self, min_priority: NotificationPriority = NotificationPriority.NORMAL) -> List[Notification]:
        """
        Used by experiences to fetch missed notifications.
        """
        return [
            n for n in self._notifications.values() 
            if not n.read and n.priority.value >= min_priority.value
        ]

    def mark_as_read(self, notification_ids: List[str]):
        for nid in notification_ids:
            if nid in self._notifications:
                self._notifications[nid].read = True
