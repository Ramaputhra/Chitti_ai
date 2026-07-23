import time
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class AnalyticsRecord:
    """
    S32A: Canonical normalized telemetry record stored in analytics.db.
    """
    record_id: str
    event_type: str        # e.g., "EXECUTION_COMPLETED", "CAPABILITY_EXECUTED", "USER_ACTIVITY"
    source_subsystem: str  # e.g., "VerificationRuntime", "ExecutionRuntime", "DesktopActivityRuntime"
    session_id: str
    timestamp: float
    duration_ms: float
    status: str            # "SUCCESS", "FAILURE", "INFO"
    payload_json: str      # Serialized event details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "event_type": self.event_type,
            "source_subsystem": self.source_subsystem,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "payload_json": self.payload_json
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalyticsRecord':
        return cls(
            record_id=data.get("record_id", ""),
            event_type=data.get("event_type", ""),
            source_subsystem=data.get("source_subsystem", ""),
            session_id=data.get("session_id", "global"),
            timestamp=data.get("timestamp", time.time()),
            duration_ms=data.get("duration_ms", 0.0),
            status=data.get("status", "INFO"),
            payload_json=data.get("payload_json", "{}")
        )

@dataclass
class UserActivityEvent:
    """
    S32B: Event published by DesktopActivityRuntime upon active application / window focus change.
    """
    app_name: str
    window_title: str
    duration_ms: float = 0.0
    session_id: str = "global"
    timestamp: float = field(default_factory=time.time)
    event_type: str = "USER_ACTIVITY"

@dataclass
class TimelineEntry:
    """
    S32C: Objective factual timeline entry preserving chronology, timestamps, application identity, and session identity.
    """
    entry_id: str
    timestamp: float
    event_type: str
    app_identity: str
    window_title: str
    duration_ms: float
    session_id: str = "global"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ActivityTimeline:
    """
    S32C: Chronological sequence of factual TimelineEntry objects.
    """
    session_id: str
    entries: List[TimelineEntry] = field(default_factory=list)
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0

    @property
    def total_entries(self) -> int:
        return len(self.entries)

@dataclass
class ActivityTimelineEntry:
    """
    S32A: Objective factual timeline entry (Rules 92 & 93 compliant).
    Legacy compatibility model mapping to TimelineEntry.
    """
    timestamp: float
    event_type: str
    title: str
    duration_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionMetrics:
    """
    S32A/S32C: Aggregated execution telemetry summary including workflow counts, durations, success/failures, replay stats.
    """
    total_executions: int = 0
    success_count: int = 0
    failure_count: int = 0
    success_rate: float = 0.0
    avg_duration_ms: float = 0.0
    replay_count: int = 0

@dataclass
class ProductivitySummary:
    """
    S32A/S32C: Objective factual session activity summary.
    """
    session_id: str
    start_time: float
    end_time: float
    total_records: int
    total_executions: int
    total_duration_sec: float
    top_events: List[str] = field(default_factory=list)

@dataclass
class InsightCard:
    """
    S32C: Pure factual analytics insight card. Contains NO interpretation, intent hypotheses, or UI code.
    """
    card_id: str
    metric_key: str
    metric_value: Any
    category: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SuggestedNarrationFacts:
    """
    S32C: Structured factual data container for future TTS/LLM narration. Contains NO generated natural language string templates or LLM prompts.
    """
    session_id: str
    top_application: str
    total_execution_count: int
    success_rate_percent: float
    replay_count: int
    most_frequent_event: str
    timestamp: float = field(default_factory=time.time)

from desktop.models.presentation import (
    PresentationBundle, BundleType, ExperienceType, SupportedRenderer
)

@dataclass
class AnalyticsPresentationBundle(PresentationBundle):
    """
    S32D: Domain presentation bundle inheriting from universal PresentationBundle.
    Aggregates ActivityTimeline, ExecutionMetrics, ProductivitySummary, InsightCard list, and SuggestedNarrationFacts.
    Contains ZERO UI rendering logic or HTML/CSS formatting.
    """
    session_id: str = "global"
    activity_timeline: Optional[ActivityTimeline] = None
    execution_metrics: Optional[ExecutionMetrics] = None
    productivity_summary: Optional[ProductivitySummary] = None
    insight_cards: List[InsightCard] = field(default_factory=list)
    suggested_narration_facts: Optional[SuggestedNarrationFacts] = None

    def __post_init__(self):
        self.bundle_type = BundleType.ANALYTICS
        self.experience_type = ExperienceType.DASHBOARD
        self.supported_renderers = [
            SupportedRenderer.DASHBOARD_RENDERER,
            SupportedRenderer.VOICE_RENDERER,
            SupportedRenderer.AVATAR_RENDERER,
            SupportedRenderer.NANO_RENDERER
        ]

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "domain_type": "ANALYTICS",
            "session_id": self.session_id,
            "activity_timeline_entries": self.activity_timeline.total_entries if self.activity_timeline else 0,
            "execution_metrics": self.execution_metrics.__dict__ if self.execution_metrics else None,
            "productivity_summary": self.productivity_summary.__dict__ if self.productivity_summary else None,
            "insight_cards_count": len(self.insight_cards),
            "suggested_narration_facts": self.suggested_narration_facts.__dict__ if self.suggested_narration_facts else None
        })
        return base_dict
