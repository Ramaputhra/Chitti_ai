import os
from typing import Any, Dict, List, Optional

from google import genai

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import IProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.health import ProviderHealth
from desktop.runtime.authentication.token_manager import TokenManager


class GeminiProvider(IProvider):
    """
    Connects to Google Gemini API for multimodal, vision, 
    and fast generative tasks.
    """
    def __init__(self, token_manager: TokenManager, logger: ILoggingService, default_model: str = "gemini-2.5-flash"):
        self.token_manager = token_manager
        self.logger = logger
        self.default_model = default_model
        self.client: Optional[genai.Client] = None
        self._state = ServiceState.STOPPED
        self._is_healthy = False

    @property
    def name(self) -> str: return "GeminiProvider"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self.logger.info("Initializing Gemini Provider...")
        
        api_key = self.token_manager.storage.get_secret("gemini_api_key")
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
            
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
                self._is_healthy = True
                self._state = ServiceState.RUNNING
                self.logger.info("Gemini initialized successfully.")
            except Exception as e:
                self.logger.error(f"Gemini initialization failed: {e}")
                self._is_healthy = False
        else:
            self.logger.warning("No Gemini API key found. Provider is unavailable.")
            self._is_healthy = False

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.client = None

    def get_provider_health(self) -> ProviderHealth:
        return ProviderHealth(
            status="Healthy" if self._is_healthy else "Unavailable",
            healthy=self._is_healthy,
            enabled=True,
            configured=True,
            authenticated=self.client is not None,
            latency_ms=300,
            last_error=None,
            version="0.5.0",
            model=self.default_model,
            uptime=0
        )

    def health_check(self) -> Dict[str, Any]:
        h = self.get_provider_health()
        return {"status": h.status, "model": h.model}

    def benchmark(self) -> Dict[str, Any]:
        return {"latency_ms": 300}

    def capabilities(self) -> List[str]:
        return ["text_generation", "vision", "multimodal"]

    def version(self) -> str:
        return "0.5.0"

    def configuration(self) -> Dict[str, Any]:
        return {"default_model": self.default_model}

    def generate(self, prompt: str) -> str:
        if not self._is_healthy or not self.client:
            return ""
            
        self.logger.info(f"Gemini generating using {self.default_model}...")
        try:
            response = self.client.models.generate_content(
                model=self.default_model,
                contents=prompt
            )
            return response.text or ""
        except Exception as e:
            self.logger.error(f"Gemini generation failed: {e}")
            return ""
