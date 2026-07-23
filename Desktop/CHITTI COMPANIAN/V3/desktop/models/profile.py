from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class UserIdentity:
    """Explicitly declared identity details. Never inferred."""
    name: str
    role: str
    languages: List[str]
    timezone: str
    explicit_preferences: List[str] # e.g., "Dark Mode", "Use technical terminology"
    declared_goals: List[str]

@dataclass
class PreferenceEvidence:
    """Explains why an adaptive preference exists (Rule 157)."""
    observation: str
    frequency: int
    confidence: float
    first_seen: datetime
    last_seen: datetime
    approved: bool

@dataclass
class AdaptivePreferences:
    """Preferences that evolve over time (e.g., answer length, speech pacing)."""
    traits: Dict[str, str] # e.g., {"speech_pacing": "fast", "toast_duration": "short"}
    evidence: Dict[str, PreferenceEvidence]

@dataclass
class ProfileRevision:
    """Auditable log of profile changes."""
    timestamp: datetime
    change: str
    reason: str
    evidence: str
    approved_by_user: bool

@dataclass
class VoiceProfile:
    preferred_voice: str = "default_en"
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0

@dataclass
class ExperienceProfile:
    morning_briefing_enabled: bool = True
    workspace_suggestions_enabled: bool = True
    proactive_suggestions_enabled: bool = False

@dataclass
class UserProfile:
    """The aggregate profile injected into AssistantContext."""
    identity: UserIdentity
    adaptive_preferences: AdaptivePreferences
    revisions: List[ProfileRevision]
    voice: VoiceProfile = field(default_factory=VoiceProfile)
    experience: ExperienceProfile = field(default_factory=ExperienceProfile)

@dataclass
class LocalRetentionPolicy:
    """Policy for local data retention."""
    conversation_retention_days: int
    analytics_retention_days: int
    artifact_retention_days: int
    memory_retention_days: int

@dataclass
class DataExportStrategy:
    """Configuration for data export capabilities."""
    export_profile: bool
    export_knowledge: bool
    export_memory: bool
    export_conversation_analytics: bool
    export_decision_history: bool
    export_settings: bool
