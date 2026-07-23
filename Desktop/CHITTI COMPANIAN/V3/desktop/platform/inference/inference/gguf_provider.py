import time
import asyncio
from desktop.app.inference_contracts import ILLMProvider
from desktop.models.inference import InferenceRequest, InferenceResponse, ProviderInfo, ProviderCapabilities, ProviderHealth, CapabilityType, CapabilityMetadata, CapabilityStatus
from desktop.services.ai.providers.gguf_provider import GGUFProvider as CoreGGUFProvider

class GGUFInferenceProvider(ILLMProvider):
    """Adapts the core GGUFProvider to the ILLMProvider interface."""
    def __init__(self):
        self.core = CoreGGUFProvider()
        
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="GGUFInferenceProvider",
            model="qwen2.5-1.5b-instruct-q4_k_m.gguf",
            capabilities=ProviderCapabilities(
                capabilities={
                    CapabilityType.STRUCTURED_OUTPUT: CapabilityMetadata(CapabilityStatus.NATIVE),
                },
                max_context=4096,
                is_local=True
            )
        )
        
    def health(self) -> ProviderHealth:
        return ProviderHealth.READY

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        start_time = time.time()
        
        messages = [{"role": "user", "content": request.prompt}]
        
        loop = asyncio.get_event_loop()
        
        # Offload blocking llama-cpp call to thread pool
        response_data = await loop.run_in_executor(
            None, 
            lambda: self.core.generate(messages, tools_enabled=False)
        )
        
        latency = (time.time() - start_time) * 1000
        return InferenceResponse(
            content=response_data.get("text", ""),
            model_used="qwen2.5-1.5b-instruct-q4_k_m.gguf",
            latency_ms=latency
        )
