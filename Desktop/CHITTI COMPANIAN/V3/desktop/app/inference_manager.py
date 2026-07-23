from typing import List, Optional
from desktop.app.inference_contracts import ILLMProvider
from desktop.models.inference import InferenceRequest, InferenceResponse, ProviderHealth

class InferenceManager:
    """
    Manages provider selection, health checks, and fallback logic.
    Ensures the Planner and Strategy are completely shielded from provider issues.
    """
    def __init__(self):
        self.providers: List[ILLMProvider] = []
        
    def register(self, provider: ILLMProvider):
        self.providers.append(provider)
        
    def get_best_provider(self, request: InferenceRequest) -> Optional[ILLMProvider]:
        """
        Selects the best available provider based on health and capabilities.
        Could be expanded to check request context window vs provider max_context.
        """
        for provider in self.providers:
            if provider.health() == ProviderHealth.READY:
                return provider
                
        # If no provider is ready, check for degraded ones
        for provider in self.providers:
            if provider.health() == ProviderHealth.DEGRADED:
                return provider
                
        return None

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        provider = self.get_best_provider(request)
        
        if not provider:
            # Shield pipeline with a safe fallback response
            print("[InferenceManager] ❌ No healthy LLM providers available.")
            return InferenceResponse(
                content='{"intent": "UnknownIntent", "confidence": 0.0}',
                model_used="fallback-offline",
                latency_ms=0.0
            )
            
        try:
            return await provider.generate(request)
        except Exception as e:
            print(f"[InferenceManager] ❌ Provider {provider.info().name} failed: {e}")
            # Try fallback to next available?
            # For now, return a safe fallback.
            return InferenceResponse(
                content='{"intent": "UnknownIntent", "confidence": 0.0}',
                model_used="fallback-error",
                latency_ms=0.0
            )
