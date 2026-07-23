from dataclasses import dataclass
from typing import Optional

@dataclass
class NarrationContext:
    domain_intent: str = "GENERAL"
    user_name: str = "boss"
    system_state: str = "NORMAL"
    workflow_id: Optional[str] = None
