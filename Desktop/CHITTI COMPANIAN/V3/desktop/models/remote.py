from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

class RemoteInteractionMode(Enum):
    SECOND_SCREEN = 1
    MONITOR = 2
    CONTROL = 3
    HANDOFF = 4
    NOTIFICATION_ONLY = 5

class PresenceState(Enum):
    ACTIVE = 1
    PASSIVE = 2
    OBSERVING = 3
    AWAY = 4
    OFFLINE = 5

class NotificationChannel(Enum):
    PUSH = 1
    TOAST = 2
    VOICE = 3
    EMAIL = 4
    SMS = 5

@dataclass
class RemoteCapabilities:
    chat: bool
    voice: bool
    notifications: bool
    workflow_control: bool
    knowledge_access: bool
    desktop_view: bool
    automation: bool
    settings: bool

@dataclass
class TrustRelationship:
    device_id: str
    trust_level: str # Trusted, Temporary, Untrusted
    verification: str # Bio, PIN, None
    paired_at: datetime
    last_verified: datetime
    revoked: bool

@dataclass
class SessionToken:
    issuer: str
    subject: str
    audience: str
    permissions: RemoteCapabilities
    device_id: str
    expiration: datetime
    signature: str
    nonce: str

@dataclass
class RemoteSession:
    session_id: str
    device_identity: TrustRelationship
    user_identity: str
    authentication: SessionToken
    transport: str
    capabilities: RemoteCapabilities
    encryption: str
    presence: PresenceState
    expires_at: datetime
    last_activity: datetime

@dataclass
class RemoteCommand:
    """Declarative intent from a remote client (Rule 169)."""
    intent: str
    arguments: Dict[str, Any]
    priority: int
    requires_confirmation: bool
    execution_scope: str
    trace_id: str

@dataclass
class RemotePolicy:
    authentication: str
    authorization: str
    risk_threshold: str # Low, Medium, High
    rate_limit: int
    audit_enabled: bool
    privacy_mode: bool

@dataclass
class InteractionContext:
    origin_device: str
    execution_owner: str
    interaction_mode: RemoteInteractionMode
    presence: PresenceState
    active_workflow: Optional[str]

@dataclass
class AuditRecord:
    timestamp: datetime
    device: str
    user: str
    intent: str
    decision: str
    policy_evaluation: str
    result: str
