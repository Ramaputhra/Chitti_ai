from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from desktop.models.conversation import ConversationArtifact

@dataclass
class Decision:
    decision_id: str
    decision: str
    decision_reason: str
    alternatives_considered: List[str]
    chosen_option: str
    decision_confidence: float
    timestamp: datetime

@dataclass
class HumanParticipants:
    people: List[str]

@dataclass
class SystemParticipants:
    applications: List[str]
    capabilities: List[str]
    repositories: List[str]
    services: List[str]
    llms: List[str]
    devices: List[str]
    os_components: List[str]

@dataclass
class ExperienceParticipants:
    human: HumanParticipants
    system: SystemParticipants

@dataclass
class EvidenceReferences:
    browser_summaries: List[str]
    vision_summaries: List[str]
    activity_artifacts: List[str]
    conversation_summaries: List[str]
    execution_results: List[str]
    presentation_artifacts: List[str]

@dataclass
class ExperienceEnvironment:
    tags: List[str]  # Home, Office, Remote, Travel, Desktop, Laptop, Meeting, Multi-monitor
    device_profile: Optional[str] = None
    operating_system: Optional[str] = None
    monitor_configuration: Optional[str] = None
    input_method: Optional[str] = None

@dataclass
class ExplainableConfidence:
    browser_confidence: float
    vision_confidence: float
    activity_confidence: float
    conversation_confidence: float
    execution_confidence: float
    overall_confidence: float

@dataclass
class SemanticScoring:
    importance: float
    novelty: float
    learning_value: float
    complexity: float
    duration_score: float
    recurrence_score: float
    priority: float

@dataclass
class ExperienceReflection:
    accomplishments: str
    remaining_work: str
    lessons_learned: str
    risks: str
    recommended_next_step: str
    open_questions: Optional[str] = None

@dataclass
class Experience(ConversationArtifact):
    """The canonical unit of cognition."""
    experience_id: str
    schema_version: str
    experience_type: str
    goal: str
    outcome: str # SUCCESS, FAILED, BLOCKED, ABANDONED, POSTPONED, PARTIALLY_COMPLETED
    status: str # ACTIVE, VALIDATED, READY_FOR_MEMORY
    start_time: datetime
    end_time: datetime
    
    decisions: List[Decision]
    participants: ExperienceParticipants
    evidence: EvidenceReferences
    environment: ExperienceEnvironment
    scoring: SemanticScoring
    confidence: ExplainableConfidence
    
    continuation_candidate: bool
    reflection: Optional[ExperienceReflection] = None
    fingerprint: Optional[str] = None
    relationships: Dict[str, List[str]] = field(default_factory=dict)
