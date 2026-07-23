from abc import ABC, abstractmethod
from typing import Optional, List
from desktop.behavior.context import BehaviorContext
from desktop.behavior.emotion_models import BehaviorTrigger
from desktop.behavior.narration_models import CommunicationIntent, SuppressionReason

class ISuppressionPolicy(ABC):
    @abstractmethod
    def evaluate(self, trigger: BehaviorTrigger, context: BehaviorContext) -> SuppressionReason:
        """
        Evaluates active system state (e.g., USER_IS_SPEAKING, BACKGROUND_TASK) 
        to determine if communication should be suppressed.
        """
        pass

class INarrationFilter(ABC):
    @abstractmethod
    def should_communicate(self, trigger: BehaviorTrigger, context: BehaviorContext) -> bool:
        """
        Evaluates the BehaviorProfile (NarrationLevel, CompanionPresenceLevel) 
        against the current trigger to decide if communication is warranted.
        """
        pass

class ICommunicationQueue(ABC):
    @abstractmethod
    def enqueue(self, intent: CommunicationIntent): pass
    
    @abstractmethod
    def coalesce_pending(self) -> List[CommunicationIntent]:
        """Merges redundant intents (e.g., multiple TASK_PROGRESS into one)."""
        pass

class INarrationRuntime(ABC):
    """
    The Silence Engine. Decides *how* and *if* CHITTI should communicate 
    based on the current BehaviorContext and active SuppressionPolicies.
    Never generates localized text.
    """
    @abstractmethod
    async def start(self): pass
    
    @abstractmethod
    async def stop(self): pass
    
    @abstractmethod
    def process_trigger(self, trigger: BehaviorTrigger, context: BehaviorContext): pass
