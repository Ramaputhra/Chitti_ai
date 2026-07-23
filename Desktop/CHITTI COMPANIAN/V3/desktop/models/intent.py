from dataclasses import dataclass, field
from typing import List
from enum import Enum
from desktop.models.workflow import WorkflowOutcome, EvidenceStrength

@dataclass
class SessionTimeline:
    events: List[str] = field(default_factory=list)

class IntentType(Enum):
    FIX_BUILD = "FIX_BUILD"
    RESEARCH_TOPIC = "RESEARCH_TOPIC"
    IMPLEMENT_FEATURE = "IMPLEMENT_FEATURE"
    DEBUG_TESTS = "DEBUG_TESTS"
    VALIDATE_CHANGES = "VALIDATE_CHANGES"
    REFACTOR_CODE = "REFACTOR_CODE"
    EXPLORE_CODEBASE = "EXPLORE_CODEBASE"

class IntentCategory(Enum):
    RESEARCH = "RESEARCH"
    IMPLEMENTATION = "IMPLEMENTATION"
    VALIDATION = "VALIDATION"
    DEBUGGING = "DEBUGGING"
    MAINTENANCE = "MAINTENANCE"
    EXPLORATION = "EXPLORATION"

@dataclass
class IntentEvidence:
    supporting_outcomes: List[WorkflowOutcome] = field(default_factory=list)
    trigger_rules: List[str] = field(default_factory=list)

@dataclass
class IntentCandidate:
    intent_type: IntentType
    category: IntentCategory
    strength: EvidenceStrength
    evidence: IntentEvidence
