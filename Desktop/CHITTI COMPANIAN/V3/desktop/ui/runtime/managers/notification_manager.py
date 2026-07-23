import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class NotificationManager:
    """
    S36D: Notification & Toast Manager rendering system overlays, toasts, and notifications.
    """
    def __init__(self):
        self.active_notifications: List[Dict[str, Any]] = []

    def show_notification(self, notification_id: str, title: str, message: str, category: str = "info") -> Dict[str, Any]:
        item = {
            "id": notification_id,
            "title": title,
            "message": message,
            "category": category,
            "dismissed": False
        }
        self.active_notifications.append(item)
        logger.info(f"[NotificationManager] Notification Shown: '{title}' [{category}]")
        return item

    def dismiss_notification(self, notification_id: str):
        self.active_notifications = [n for n in self.active_notifications if n["id"] != notification_id]
        logger.info(f"[NotificationManager] Notification Dismissed: '{notification_id}'")
