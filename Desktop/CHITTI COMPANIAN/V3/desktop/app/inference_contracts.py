from abc import ABC, abstractmethod
from desktop.models.inference import InferenceRequest, InferenceResponse, InferenceResult, ProviderInfo, ProviderHealth
from desktop.models.interaction import InteractionEnvelope
from desktop.models.memory import MemorySnapshot

class ILLMProvider(ABC):
    """
    Abstracts the connection to an LLM (e.g. Mock, Ollama, OpenAI).
    """
    @abstractmethod
    def info(self) -> ProviderInfo:
        pass
        
    @abstractmethod
    def health(self) -> ProviderHealth:
        pass

    @abstractmethod
    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        pass

class IInferenceStrategy(ABC):
    """
    Converts user interaction and memory into a pure InferenceResult.
    (Rule 183: Inference produces decisions, never side effects.)
    """
    @abstractmethod
    async def infer(self, interaction: InteractionEnvelope, memory: MemorySnapshot) -> InferenceResult:
        pass
