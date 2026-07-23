from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SyncScope(Enum):
    LOCAL = 1
    PERSONAL = 2
    TEAM = 3
    ORGANIZATION = 4

class ConflictPolicy(Enum):
    LWW = 1 # Last Writer Wins (Configuration)
    EVENT_REPLAY = 2 # Append-only (Knowledge)
    SINGLE_OWNER = 3 # Handoff (Execution)

class TransportProvider(Enum):
    LAN = 1
    CLOUD = 2
    USB = 3
    BLUETOOTH = 4
    FUTURE = 5

class ExecutionDisposition(Enum):
    CONTINUE = 1
    MONITOR = 2
    PAUSE = 3
    TRANSFER = 4
    CANNOT_TRANSFER = 5

@dataclass
class DevicePresence:
    active: bool
    idle: bool
    offline: bool
    charging: bool
    network: str
    last_activity: datetime

@dataclass
class ReplicaIdentity:
    device_id: str
    user_id: str
    instance_id: str
    generation: int
    last_seen: datetime

@dataclass
class DeviceCapability:
    platform: str
    execution_engines: List[str] # e.g., ["Playwright", "Terminal", "Compiler"]
    observation_sensors: List[str]
    memory_capacity: str
    gpu_available: bool
    network_interfaces: List[str]
    permissions: List[str]

@dataclass
class SyncManifest:
    """Declarative synchronization policy."""
    resource: str
    scope: SyncScope
    direction: str # Bidirectional, Local-Only, Upload-Only
    ownership: str
    conflict_policy: ConflictPolicy
    retention: str
    encryption: str
    requires_consent: bool

@dataclass
class HandoffState:
    """Portable snapshot for transferring execution (Rule 158)."""
    goal: str
    workflow_id: str
    active_step: str
    workspace_snapshot: str
    context_transition: str
    pending_constraints: List[str]
    resume_token: str # Deterministic continuation
    expires_at: datetime
    execution_owner: str # Ensures Rule 159 (Single Owner)
