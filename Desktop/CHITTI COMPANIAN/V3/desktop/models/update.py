from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

class UpdateDisposition(Enum):
    WAIT = 1
    PAUSE_AND_RESUME = 2
    PREEMPT = 3
    DEFER = 4
    FORCE_SECURITY = 5

class UpdateChannel(Enum):
    STABLE = 1
    BETA = 2
    NIGHTLY = 3
    SECURITY = 4

@dataclass
class UpdatePolicy:
    channel: UpdateChannel
    maintenance_window: str # e.g., "02:00-04:00"
    security_policy: str # Immediate, Scheduled
    plugin_policy: str # Auto, Notify
    rollback_policy: str # AutoRollbackOnFailure
    battery_policy: str # RequirePluggedIn
    network_policy: str # WifiOnly

@dataclass
class UpdateManifest:
    id: str
    component: str # Core, Plugin, Model
    version: str
    channel: UpdateChannel
    signature: str
    dependencies: List[str]
    schema_version: str
    migration_plan: str
    rollback_supported: bool
    restart_required: bool
    breaking_change: bool
    release_notes: str
    minimum_platform_version: str
    hot_swappable: bool

@dataclass
class RecoveryPoint:
    """Comprehensive platform state (Rule 165)."""
    id: str
    platform_version: str
    runtime_versions: Dict[str, str]
    database_snapshot_path: str
    plugin_versions: Dict[str, str]
    active_workflows: List[str]
    handoff_token: str
    configuration: Dict[str, Any]
    timestamp: datetime

@dataclass
class CompatibilityReport:
    platform_compatible: bool
    plugins_compatible: bool
    models_compatible: bool
    database_migration_required: bool
    settings_compatible: bool
    warnings: List[str]

@dataclass
class PlatformHealthCheck:
    runtime_health: bool
    plugin_health: bool
    model_health: bool
    database_health: bool
    workflow_health: bool
    passed: bool

@dataclass
class UpdateTransaction:
    """Ensures partial updates never corrupt the system (Rule 165)."""
    id: str
    components: List[str]
    status: str # Staging, Migrating, Committing, RolledBack, Completed
    current_phase: str
    recovery_point: Optional[RecoveryPoint]
    duration_ms: int
    failure_reason: Optional[str]
