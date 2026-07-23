import json
import time
import requests
from desktop.app.inference_contracts import ILLMProvider
from desktop.models.inference import InferenceRequest, InferenceResponse, ProviderInfo, ProviderCapabilities, ProviderHealth, CapabilityType, CapabilityMetadata, CapabilityStatus

class OllamaProvider(ILLMProvider):
    """
    Real local LLM Provider via Ollama's REST API.
    """
    def __init__(self, host: str = "http://localhost:11434", default_model: str = "llama3"):
        self.host = host
        self.default_model = default_model
        
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="OllamaProvider",
            model=self.default_model,
            capabilities=ProviderCapabilities(
                capabilities={
                    CapabilityType.STRUCTURED_OUTPUT: CapabilityMetadata(CapabilityStatus.NATIVE),
                    CapabilityType.STREAMING: CapabilityMetadata(CapabilityStatus.NATIVE),
                    CapabilityType.MULTIMODAL: CapabilityMetadata(CapabilityStatus.UNSUPPORTED),
                    CapabilityType.FUNCTION_CALLING: CapabilityMetadata(CapabilityStatus.EXPERIMENTAL),
                },
                max_context=8192,
                is_local=True
            )
        )
        
    def health(self) -> ProviderHealth:
        try:
            resp = requests.get(f"{self.host}/api/version", timeout=1.0)
            if resp.status_code == 200:
                return ProviderHealth.READY
        except Exception:
            pass
        return ProviderHealth.UNAVAILABLE

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        start_time = time.time()
        
        payload = {
            "model": request.model_hint or self.default_model,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature
            }
        }
        
        if request.system_prompt:
            payload["system"] = request.system_prompt
            
        if request.json_mode:
            payload["format"] = "json"
            
        try:
            # We use requests here synchronously for simplicity, 
            # in a real high-throughput system we'd use aiohttp.
            # We can use asyncio.to_thread if we want to avoid blocking the event loop entirely.
            import asyncio
            response = await asyncio.to_thread(
                requests.post, 
                f"{self.host}/api/generate", 
                json=payload, 
                timeout=request.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            latency = (time.time() - start_time) * 1000
            
            return InferenceResponse(
                content=data.get("response", ""),
                model_used=data.get("model", self.default_model),
                latency_ms=latency,
                usage={
                    "eval_count": data.get("eval_count", 0),
                    "eval_duration": data.get("eval_duration", 0)
                }
            )
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama request failed: {e}")
