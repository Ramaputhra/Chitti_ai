from abc import ABC, abstractmethod
from desktop.core.config.schema import IntentSchema, WorkflowSchema, NormalizationSchema
from desktop.core.eventbus import IEventBus
from typing import Optional, List

class IConfigProvider(ABC):
    @abstractmethod
    def get_intent(self, intent_id: str) -> Optional[IntentSchema]: pass
    
    @abstractmethod
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowSchema]: pass

class INormalizationProvider(ABC):
    @abstractmethod
    def normalize(self, text: str) -> str: pass

class IIntentRegistry(ABC):
    @abstractmethod
    def find_match(self, text: str) -> Optional[str]: pass
