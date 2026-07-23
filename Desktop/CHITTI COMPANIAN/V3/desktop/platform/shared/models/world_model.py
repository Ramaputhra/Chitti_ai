from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from desktop.platform.shared.models.entity import ResolvedPerson

@dataclass
class WorldState:
    """
    Represents the derived, high-level situational awareness of the environment.
    This is projected from Observation History and never mutated manually by any runtime.
    """
    desk_occupied: bool = False
    current_occupant: Optional[ResolvedPerson] = None
    active_workspace: Optional[str] = None
    meeting_active: bool = False
    
    # Store raw metrics for planner context if needed
    occupant_active_duration: float = 0.0
    workspace_active_duration: float = 0.0
    
    revision: int = 1

    def to_dict(self) -> Dict[str, Any]:
        occupant_data = None
        if self.current_occupant:
            occupant_data = self.current_occupant.__dict__.copy() if hasattr(self.current_occupant, "__dict__") else dict(self.current_occupant)
            
        return {
            "desk_occupied": self.desk_occupied,
            "current_occupant": occupant_data,
            "active_workspace": self.active_workspace,
            "meeting_active": self.meeting_active,
            "occupant_active_duration": self.occupant_active_duration,
            "workspace_active_duration": self.workspace_active_duration,
            "revision": self.revision
        }
