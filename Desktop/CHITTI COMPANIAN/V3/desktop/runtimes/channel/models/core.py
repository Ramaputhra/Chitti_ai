from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

class ChannelType(Enum):
    VOICE = "voice"
    DESKTOP_UI = "desktop_ui"
    MOBILE_CHAT = "mobile_chat"

class SessionState(Enum):
    DISCONNECTED = "Disconnected"
    CONNECTING = "Connecting"
    CONNECTED = "Connected"
    ACTIVE = "Active"
    TIMEOUT = "Timeout"

class HeartbeatState(Enum):
    HEALTHY = "Healthy"
    WEAK = "Weak"
    LOST = "Lost"

class PresenceState(Enum):
    DESKTOP_ACTIVE = "Desktop Active"
    MOBILE_ACTIVE = "Mobile Active"
    DISCONNECTED = "Disconnected"
    IDLE = "Idle"
    BUSY = "Busy"
    DO_NOT_DISTURB = "Do Not Disturb"

class TransferState(Enum):
    QUEUED = "Queued"
    TRANSFERRING = "Transferring"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    FAILED = "Failed"

class DeviceType(Enum):
    PHONE = "Phone"
    TABLET = "Tablet"
    DESKTOP_CLIENT = "Desktop Client"

class NotificationPriority(Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    PROGRESS = "PROGRESS"
    ACTION_REQUIRED = "ACTION_REQUIRED"

@dataclass
class HandshakeVersion:
    protocol_version: str = "1.0.0"
    app_version: str = "1.0.0"
    supported_features: List[str] = field(default_factory=lambda: [
        "chat", "notifications", "workflow_progress", "downloads", "screenshot", "remote_approval"
    ])

@dataclass
class TrustedDevice:
    device_id: str
    device_name: str
    user_id: str
    public_key: str
    permanent_token: str
    device_type: str = "Phone"
    trust_level: str = "Full"
    trust_status: str = "Active" # Active, Revoked, Temporary
    pair_date: datetime = field(default_factory=datetime.utcnow)
    last_connected: datetime = field(default_factory=datetime.utcnow)
    last_known_ip: str = "127.0.0.1"
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)

