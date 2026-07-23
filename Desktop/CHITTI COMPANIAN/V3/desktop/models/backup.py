from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

class BackupClass(Enum):
    ESSENTIAL = 1
    RECOVERABLE = 2
    EPHEMERAL = 3

class BackupMode(Enum):
    FULL = 1
    INCREMENTAL = 2
    DIFFERENTIAL = 3

class BackupTarget(Enum):
    LOCAL = 1
    EXTERNAL = 2
    NAS = 3
    PERSONAL_CLOUD = 4
    ENTERPRISE = 5
    MULTIPLE = 6

class SerializationFormat(Enum):
    SQLITE = 1
    JSON = 2
    MARKDOWN = 3
    ZIP = 4
    ENCRYPTED_BUNDLE = 5

class ExportProfile(Enum):
    KNOWLEDGE_ARCHIVE = 1
    PROFILE_ARCHIVE = 2
    PROJECT_ARCHIVE = 3
    FULL_SYSTEM = 4
    PORTABLE_WORKSPACE = 5

@dataclass
class RetentionPolicy:
    hourly: int
    daily: int
    weekly: int
    monthly: int
    yearly: int
    max_storage_gb: float
    deduplication: bool
    pruning_strategy: str

@dataclass
class BackupPolicy:
    targets: List[BackupTarget]
    encryption: bool
    redundancy: int
    verification: bool
    bandwidth_limit_mbps: float

@dataclass
class BackupManifest:
    id: str
    version: str
    created_at: datetime
    platform_version: str
    components: List[str]
    schema_versions: Dict[str, str]
    encryption: str
    compression: str
    integrity_hash: str
    retention_class: str
    dependencies: List[str]

@dataclass
class BackupIntegrity:
    """Every restore should validate this before proceeding (Rule 168)."""
    checksum: str
    signature: str
    verification_time: datetime
    verified_by: str
    corruption_detected: bool

@dataclass
class RestorePlan:
    backup_id: str
    target_version: str
    components: List[str]
    conflicts: List[str]
    migrations: List[str]
    estimated_duration_ms: int

@dataclass
class ContentObject:
    """Content-addressable storage for large artifacts."""
    hash: str
    size_bytes: int
    references: int
