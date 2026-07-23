from typing import Optional
from desktop.models.companion import ActivityMemoryModel

class ActivityResolver:
    """
    Provides an abstraction layer over MemoryRuntime for the Planner.
    Allows fetching activity by various logical criteria without 
    coupling the Planner to raw SQL or Memory primitives.
    """
    
    def __init__(self, memory_runtime):
        self.memory_runtime = memory_runtime
        
    def get_latest_project(self) -> Optional[ActivityMemoryModel]:
        """Returns the most recent Coding activity."""
        if hasattr(self.memory_runtime, 'get_latest_activity'):
            return self.memory_runtime.get_latest_activity(domain="Coding")
        return None
