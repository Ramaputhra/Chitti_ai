from typing import Optional
import time
import abc
import urllib.request
import urllib.error
import json

from desktop.models.lifecycle import IRuntime
from desktop.app.context import KernelContext
from desktop.models.events import SystemEvent
from desktop.models.inference import InferenceRequest, InferenceTelemetry
from desktop.infrastructure.prompt_builder import PromptBuilder
from desktop.infrastructure.response_validator import ResponseValidator

class InferenceEvent(SystemEvent):
    def __init__(self, name: str, data: dict):
        super().__init__(name, data)

class LLMProvider(abc.ABC):
    @abc.abstractmethod
    def name(self) -> str:
        pass
        
    @abc.abstractmethod
    async def generate(self, prompt: str, temperature: float, max_tokens: int) -> dict:
        """Returns {'text': ..., 'input_tokens': ..., 'output_tokens': ..., 'finish_reason': ...}"""
        pass

class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, name: str, base_url: str, model: str):
        self._name = name
        self.base_url = base_url
        self.model = model
        
    def name(self) -> str:
        return f"{self._name} ({self.model})"
        
    async def generate(self, prompt: str, temperature: float, max_tokens: int) -> dict:
        # MVP blocking call wrapper (should use aiohttp in production)
        req_data = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }).encode("utf-8")
        
        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode())
                text = res_data["choices"][0]["message"]["content"]
                finish_reason = res_data["choices"][0].get("finish_reason", "stop")
                usage = res_data.get("usage", {})
                
                return {
                    "text": text,
                    "input_tokens": usage.get("prompt_tokens", PromptBuilder._estimate_tokens(prompt)),
                    "output_tokens": usage.get("completion_tokens", PromptBuilder._estimate_tokens(text)),
                    "finish_reason": finish_reason
                }
        except Exception as e:
            return {"error": str(e)}

class ProviderManager:
    def __init__(self):
        self.providers = {}
        self.active_provider = None
        
    def register_provider(self, id: str, provider: LLMProvider):
        self.providers[id] = provider
        if not self.active_provider:
            self.active_provider = provider
            
    def set_active(self, id: str):
        if id in self.providers:
            self.active_provider = self.providers[id]

class InferenceRuntime(IRuntime):
    """
    Rule 34: Only the Inference Runtime may assemble prompts for language models.
    """
    def __init__(self, provider_manager: ProviderManager):
        self.provider_manager = provider_manager
        self._running = False
        self.context: Optional[KernelContext] = None
        
    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        return True
        
    async def start(self):
        self._running = True
        
    async def stop(self):
        self._running = False
            
    async def shutdown(self):
        pass

    async def generate(self, request: InferenceRequest) -> str:
        start_time = time.time()
        
        # 1. Assemble prompt via pure PromptBuilder
        prompt = PromptBuilder.build(request)
        
        # 2. Execute via active provider
        provider = self.provider_manager.active_provider
        if not provider:
            raise Exception("No active LLM Provider configured.")
            
        result = await provider.generate(prompt, request.temperature, request.max_tokens)
        
        latency = (time.time() - start_time) * 1000
        
        if "error" in result:
            telemetry = InferenceTelemetry(
                provider=provider.name(), model=provider.name(), latency_ms=latency,
                input_tokens=0, output_tokens=0, cached=False, temperature=request.temperature,
                finish_reason="error", error=result["error"]
            )
            await self._publish_telemetry(telemetry)
            return "Error calling inference provider."
            
        raw_text = result["text"]
        
        # 3. Validate
        validated_text = ResponseValidator.validate(raw_text)
        
        # 4. Telemetry
        telemetry = InferenceTelemetry(
            provider=provider.name(), model=provider.name(), latency_ms=latency,
            input_tokens=result["input_tokens"], output_tokens=result["output_tokens"],
            cached=False, temperature=request.temperature, finish_reason=result["finish_reason"]
        )
        await self._publish_telemetry(telemetry)
        
        return validated_text
        
    async def _publish_telemetry(self, telemetry: InferenceTelemetry):
        if self.context and self.context.event_bus:
            await self.context.event_bus.publish("InferenceTelemetryEvent", InferenceEvent("InferenceTelemetryEvent", telemetry.__dict__))
