from enum import Enum
from dataclasses import dataclass, field
import time

class NotificationPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class NotificationSource(Enum):
    SYSTEM = "SYSTEM"
    EMAIL = "EMAIL"
    CALENDAR = "CALENDAR"
    APPLICATION = "APPLICATION"

class NotificationCategory(Enum):
    SYSTEM = "SYSTEM"
    EMAIL = "EMAIL"
    CALENDAR = "CALENDAR"
    APPLICATION = "APPLICATION"
    MESSAGE = "MESSAGE"
    SECURITY = "SECURITY"

@dataclass
class Notification:
    id: str
    source: NotificationSource
    category: NotificationCategory
    title: str
    body: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    received_at: float = field(default_factory=time.time)
    read: bool = False
    actionable: bool = False
    metadata: dict = field(default_factory=dict)
