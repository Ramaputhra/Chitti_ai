from abc import ABC, abstractmethod
from typing import List
from desktop.behavior.models import BehaviorProfile, BehaviorState

class IBehaviorManager(ABC):
    """
    The apex layer of Phase 6. Maintains global behavior state and publishes updates 
    to the downstream Emotion, Narration, Character, and Expression runtimes.
    """
    
    @abstractmethod
    async def start(self): pass
    
    @abstractmethod
    async def stop(self): pass

    @abstractmethod
    def set_active_profile(self, profile: BehaviorProfile):
        """Sets the static profile and broadcasts BehaviorProfileChanged."""
        pass
        
    @abstractmethod
    def get_active_profile(self) -> BehaviorProfile:
        pass
        
    @abstractmethod
    def get_current_state(self) -> BehaviorState:
        """Returns the volatile state of the behavior engine."""
        pass

    @abstractmethod
    def register_available_capabilities(self, capabilities: List[str]):
        """
        Allows the BehaviorManager to be aware of what capabilities exist 
        (e.g. to fallback to TEXT_ONLY mode if TTS capability dies).
        """
        pass
