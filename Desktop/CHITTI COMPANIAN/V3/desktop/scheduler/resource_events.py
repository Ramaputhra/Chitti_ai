from dataclasses import dataclass
from desktop.models.events import SystemEvent

@dataclass
class ResourceAcquired(SystemEvent):
    event_type: str = "ResourceAcquired"
    workflow_id: str = ""
    node_id: str = ""
    resource_id: str = ""
    lock_id: str = ""

@dataclass
class ResourceReleased(SystemEvent):
    event_type: str = "ResourceReleased"
    workflow_id: str = ""
    node_id: str = ""
    resource_id: str = ""
    lock_id: str = ""

@dataclass
class ResourceBlocked(SystemEvent):
    event_type: str = "ResourceBlocked"
    workflow_id: str = ""
    node_id: str = ""
    resource_id: str = ""
    priority: int = 0
    wait_start_time: float = 0.0

@dataclass
class ResourceExpired(SystemEvent):
    event_type: str = "ResourceExpired"
    workflow_id: str = ""
    node_id: str = ""
    resource_id: str = ""
    lock_id: str = ""

@dataclass
class ResourceRevoked(SystemEvent):
    event_type: str = "ResourceRevoked"
    workflow_id: str = ""
    node_id: str = ""
    resource_id: str = ""
    lock_id: str = ""
    reason: str = ""
