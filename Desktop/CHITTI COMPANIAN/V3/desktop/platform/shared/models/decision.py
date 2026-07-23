import uuid
from typing import Optional, Any, Dict
from dataclasses import dataclass, field
from datetime import datetime
from desktop.runtimes.prediction.models import Forecast

@dataclass
class Decision:
    """
    A foundational platform concept representing an executive choice made by the Planner.
    It bridges the gap between intelligence (Forecasts) and execution (Capabilities).
    """
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reason: str = ""
    selected_forecast: Optional[Forecast] = None
    selected_capability: Optional[str] = None
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    expected_outcome: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
