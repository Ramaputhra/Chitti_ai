from typing import Generator, List

from desktop.platform.shared.interfaces.provider import IProvider
from desktop.platform.shared.models.ai import LLMRequest, LLMResponse, ResponseChunk
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class HealthStatus:
    status: str  # "HEALTHY", "DEGRADED", "FAILED"
    loaded_model: str
    context_size: int
    gpu_enabled: bool
    memory_usage: Optional[float]
    last_error: Optional[str]


class ILLMProvider(IProvider):
    """
    Standard interface for all LLM inference engines (Gemini, OpenAI, Ollama).
    Must strictly accept LLMRequest and yield ResponseChunk or LLMResponse.
    """
    def list_models(self) -> List[str]:
        ...

    def stream(self, request: LLMRequest) -> Generator[ResponseChunk, None, None]:
        ...

    def complete(self, request: LLMRequest) -> LLMResponse:
        ...

    def capabilities(self) -> List[str]:
        ...
        
    def health_check(self) -> HealthStatus:
        ...
        
    def generate_stream(self, messages: List[Dict[str, str]], tools_enabled: bool = True) -> Generator[Dict[str, Any], None, None]:
        ...
