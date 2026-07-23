import json
from typing import Any, Dict, Generator, List

from desktop.platform.shared.interfaces.llm import ILLMProvider
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import ProviderStatus
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import LLMRequest, LLMResponse, ResponseChunk


class MockLLMProvider(ILLMProvider):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "MockLLMProvider"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> Dict[str, Any]:
        return {"status": "HEALTHY"}

    def benchmark(self) -> Dict[str, Any]:
        return {"latency_ms": 250, "tokens_per_sec": 45}

    def load_model(self, model_path: str) -> bool:
        return True

    def unload_model(self) -> None:
        pass

    def supports_streaming(self) -> bool:
        return True

    def supports_gpu(self) -> bool:
        return False

    def get_status(self) -> ProviderStatus:
        return ProviderStatus.HEALTHY

    def list_models(self) -> List[str]:
        return ["mock-llm-1.0"]

    def _generate_mock_json(self) -> str:
        return json.dumps({
            "version": 1,
            "tool": {
                "name": "GreetingTool",
                "arguments": {}
            },
            "response": "Hello, I am processing your request."
        })

    def stream(self, request: LLMRequest) -> Generator[ResponseChunk, None, None]:
        self.logger.info("MockLLMProvider streaming mock response")
        text = self._generate_mock_json()
        # Stream character by character for testing
        for char in text:
            yield ResponseChunk(text=char, is_final=False)
        yield ResponseChunk(text="", is_final=True)

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.logger.info("MockLLMProvider generating complete response")
        return LLMResponse(
            text="Hello, I am processing your request.",
            raw_json=self._generate_mock_json(),
            latency_ms=250.0
        )
