import os
from typing import Any, Dict, List, Optional

from openai import OpenAI

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import IProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.health import ProviderHealth
from desktop.runtime.authentication.token_manager import TokenManager


class OpenAIProvider(IProvider):
    """
    Connects to OpenAI for advanced reasoning, complex Planner logic,
    and fallback semantic extraction.
    """
    def __init__(self, token_manager: TokenManager, logger: ILoggingService, default_model: str = "gpt-4o"):
        self.token_manager = token_manager
        self.logger = logger
        self.default_model = default_model
        self.client: Optional[OpenAI] = None
        self._state = ServiceState.STOPPED
        self._is_healthy = False

    @property
    def name(self) -> str: return "OpenAIProvider"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self.logger.info("Initializing OpenAI Provider...")
        
        # Priority: 1. Secure Storage -> 2. Environment Variable
        api_key = self.token_manager.storage.get_secret("openai_api_key")
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")
            
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                # Verify token works
                self.client.models.list()
                self._is_healthy = True
                self._state = ServiceState.RUNNING
                self.logger.info("OpenAI initialized successfully.")
            except Exception as e:
                self.logger.error(f"OpenAI initialization failed: {e}")
                self._is_healthy = False
        else:
            self.logger.warning("No OpenAI API key found. Provider is unavailable.")
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
            latency_ms=400,
            last_error=None,
            version="1.14.0",
            model=self.default_model,
            uptime=0
        )

    def health_check(self) -> Dict[str, Any]:
        h = self.get_provider_health()
        return {"status": h.status, "model": h.model}

    def benchmark(self) -> Dict[str, Any]:
        return {"latency_ms": 400}  # Network bounded

    def capabilities(self) -> List[str]:
        return ["text_generation", "tool_calling", "complex_reasoning", "vision"]

    def version(self) -> str:
        return "1.14.0"

    def configuration(self) -> Dict[str, Any]:
        return {"default_model": self.default_model}

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self._is_healthy or not self.client:
            return ""
            
        self.logger.info(f"OpenAI generating using {self.default_model}...")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=messages
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            self.logger.error(f"OpenAI generation failed: {e}")
            return ""
