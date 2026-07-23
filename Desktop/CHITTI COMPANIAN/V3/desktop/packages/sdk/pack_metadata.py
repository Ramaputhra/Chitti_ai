from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from enum import Enum

class VerificationLevel(Enum):
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"

@dataclass
class CapabilityMetadata:
    """Universal capability quality, category, and automation hooks metadata."""
    category: str = "Uncategorized" # e.g. Navigation, Observation, Organization, Discovery
    verification_level: VerificationLevel = VerificationLevel.STANDARD
    
    # Automation Hooks
    supports_streaming: bool = False
    supports_pause: bool = False
    supports_resume: bool = False
    supports_cancel: bool = False
    supports_background: bool = False
    supports_schedule: bool = False
    supports_undo: bool = False
    undo_action: Optional[str] = None
    
    # Quality & Constraints
    stability: str = "stable" # experimental, beta, stable
    estimated_latency: str = "low" # low, medium, high
    offline_capable: bool = True
    requires_network: bool = False
    requires_user_confirmation: bool = False
    produces_artifacts: bool = False
