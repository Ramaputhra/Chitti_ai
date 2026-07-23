from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from desktop.models.environment import EnvironmentSession, AuthenticationContext

@dataclass
class CommunicationSession(EnvironmentSession):
    """
    Base session for all communication environments.
    Rule 362: Long-running conversations, subscriptions, and API auth belong here, never Engines.
    """
    auth_context: Optional[AuthenticationContext] = None
    active_subscriptions: Dict[str, Any] = field(default_factory=dict)
    rate_limits: Dict[str, int] = field(default_factory=dict)
    provider_metadata: Dict[str, Any] = field(default_factory=dict)
    cached_resources: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EmailSession(CommunicationSession):
    inbox_sync_state: str = ""
    active_drafts: List[str] = field(default_factory=list)

@dataclass
class CalendarSession(CommunicationSession):
    calendar_sync_state: str = ""
    tracked_events: List[str] = field(default_factory=list)

@dataclass
class APISession(CommunicationSession):
    base_url: str = ""
    active_webhooks: List[str] = field(default_factory=list)
