from abc import ABC, abstractmethod
from typing import List, Optional
from desktop.behavior.context import BehaviorContext
from desktop.behavior.narration_models import CommunicationIntent
from desktop.behavior.character_models import DialogueContent, FinalDialogue

class ITemplateEngine(ABC):
    @abstractmethod
    def load_templates(self, language: str, intent_id: str) -> List[dict]:
        """Loads JSON templates from localized directories (e.g., dialogues/en/task_started.json)."""
        pass

class IDialogueSelector(ABC):
    @abstractmethod
    def select_variant(self, templates: List[dict], context: BehaviorContext) -> dict:
        """
        Deterministically filters and selects a template variant based on 
        SpeechStyle, Emotion, HumorLevel, and predefined Dialogue Rules (e.g., duration > 5 sec).
        """
        pass

class IVariableInjector(ABC):
    @abstractmethod
    def inject_safe_variables(self, template_text: str, current_state: dict) -> str:
        """Interpolates text using ONLY the predefined SAFE_VARIABLES whitelist."""
        pass

class IAntiRepetitionFilter(ABC):
    @abstractmethod
    def evaluate(self, dialogue_id: str) -> bool:
        """
        Checks the recent dialogue memory (e.g., last 20 dialogue ids).
        Returns False if the dialogue was recently spoken (suppresses output).
        """
        pass

class ICharacterRuntime(ABC):
    """
    Consumes CommunicationIntent, routes it through the synthesis pipeline, 
    and publishes the FinalDialogueGenerated event for TTS and Expression runtimes.
    """
    @abstractmethod
    async def process_communication_queue(self):
        """Pulls intents from CommunicationQueue and delegates to synthesis."""
        pass
        
    @abstractmethod
    def synthesize_dialogue(self, intent: CommunicationIntent, context: BehaviorContext) -> Optional[FinalDialogue]:
        pass
