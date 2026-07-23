from abc import ABC, abstractmethod
from typing import List, Optional
from desktop.behavior.context import EmotionState, BehaviorContext
from desktop.behavior.emotion_models import EmotionSnapshot, BehaviorTrigger, TimelineEntry
from desktop.behavior.models import BehaviorProfile

class IEmotionStateEngine(ABC):
    @abstractmethod
    def evaluate_transition(
        self, 
        current_snapshot: EmotionSnapshot, 
        trigger: BehaviorTrigger, 
        profile: BehaviorProfile,
        reason: str
    ) -> EmotionSnapshot:
        """
        Uses a configuration-driven transition matrix. 
        If the trigger maps to the same EmotionState, it increases the intensity (Emotional Momentum) 
        rather than initiating a brand new emotional transition.
        """
        pass

class IBehaviorTimeline(ABC):
    @abstractmethod
    def append(self, entry: TimelineEntry): pass
    
    @abstractmethod
    def get_recent(self, limit: int = 10) -> List[TimelineEntry]: pass

class IEmotionRuntime(ABC):
    """
    The central intelligence of the Behavior Layer.
    Subscribes to EventBus, uses TriggerMapper to filter events, 
    and uses StateEngine to compute the new EmotionSnapshot, which is then published.
    """
    
    @abstractmethod
    async def start(self): pass
    
    @abstractmethod
    async def stop(self): pass
    
    @abstractmethod
    def get_current_snapshot(self, conversation_id: str) -> EmotionSnapshot: pass
