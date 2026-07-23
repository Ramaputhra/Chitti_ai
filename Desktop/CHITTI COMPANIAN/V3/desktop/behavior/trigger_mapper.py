from abc import ABC, abstractmethod
from typing import Optional
from desktop.models.events import SystemEvent
from desktop.behavior.emotion_models import BehaviorTrigger

class IBehaviorTriggerMapper(ABC):
    """
    Acts as a whitelist filter and semantic mapper between raw execution events 
    and behavior triggers. Isolates the Emotion Runtime from changing execution internals.
    """
    
    @abstractmethod
    def map_event(self, event: SystemEvent) -> Optional[BehaviorTrigger]:
        """
        Returns a mapped BehaviorTrigger if the event is whitelisted and relevant.
        Returns None if the event should be ignored by the Behavior Layer.
        """
        pass
