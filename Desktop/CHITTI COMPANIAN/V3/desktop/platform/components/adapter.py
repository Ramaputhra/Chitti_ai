from abc import ABC, abstractmethod
from typing import Any
from desktop.models.component_states import HealthState
from desktop.models.ai_context import RuntimeContext
from desktop.models.ai_result import AIResult

class ProviderAdapter(ABC):
    """
    The abstraction contract for all Inference and Execution Backends.
    This interface ensures the rest of CHITTI never couples to specific 
    libraries like Transformers, ONNX, or llama.cpp.
    """
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the adapter resources (e.g. allocate memory, load backend)."""
        pass
        
    @abstractmethod
    def health_check(self) -> HealthState:
        """Return the current operational health of the provider."""
        pass
        
    @abstractmethod
    def warm(self) -> None:
        """Pre-warm the model or backend (e.g. compile kernels, load weights to VRAM)."""
        pass
        
    @abstractmethod
    def execute(self, payload: Any, context: RuntimeContext) -> AIResult[Any]:
        """
        Execute the primary capability of this provider.
        Must be completely stateless and thread-safe.
        """
        pass
        
    @abstractmethod
    def unload(self) -> None:
        """Unload weights, clear VRAM, and release locks."""
        pass
