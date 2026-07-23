from enum import Enum
from typing import Any, Dict, List

from desktop.platform.shared.interfaces.service import IService


class ProviderStatus(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


from desktop.platform.shared.models.health import ProviderHealth

class IProvider(IService):
    """
    Base interface for all dynamically routable providers (STT, TTS, LLM, Vision, etc).
    """
    def get_provider_health(self) -> ProviderHealth:
        ...
    def benchmark(self) -> Dict[str, Any]:
        ...

    def capabilities(self) -> List[str]:
        ...

    def version(self) -> str:
        ...

    def configuration(self) -> Dict[str, Any]:
        ...

    def load_model(self, model_path: str) -> bool:
        ...

    def unload_model(self) -> None:
        ...

    def supports_streaming(self) -> bool:
        ...

    def supports_gpu(self) -> bool:
        ...

    def get_status(self) -> ProviderStatus:
        ...


class IProviderRegistry(IService):
    """
    Generic registry to hold enabled/disabled states for a specific category of providers.
    """
    def register_provider(self, provider: IProvider, enabled: bool = True) -> None:
        ...

    def get_provider(self, name: str) -> IProvider:
        ...

    def get_active_providers(self) -> List[IProvider]:
        ...

    def enable_provider(self, name: str) -> None:
        ...

    def disable_provider(self, name: str) -> None:
        ...
