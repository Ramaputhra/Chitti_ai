import json
from desktop.app.inference_contracts import ILLMProvider
from desktop.models.inference import InferenceRequest, InferenceResponse, ProviderInfo, ProviderCapabilities, ProviderHealth, CapabilityType, CapabilityMetadata, CapabilityStatus

class MockLLMProvider(ILLMProvider):
    """
    Simulates an LLM for deterministic testing of the inference strategy (Sprint 83).
    Returns JSON strings mimicking expected LLM outputs.
    """
    
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="MockLLMProvider",
            model="mock-llm-1.0",
            capabilities=ProviderCapabilities(
                capabilities={
                    CapabilityType.STRUCTURED_OUTPUT: CapabilityMetadata(CapabilityStatus.NATIVE),
                    CapabilityType.STREAMING: CapabilityMetadata(CapabilityStatus.UNSUPPORTED),
                    CapabilityType.MULTIMODAL: CapabilityMetadata(CapabilityStatus.UNSUPPORTED),
                    CapabilityType.FUNCTION_CALLING: CapabilityMetadata(CapabilityStatus.UNSUPPORTED),
                },
                max_context=4096,
                is_local=True
            )
        )
        
    def health(self) -> ProviderHealth:
        return ProviderHealth.READY

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        prompt_lower = request.prompt.lower()
        
        # Tier 1: Deterministic
        if "hello" in prompt_lower:
            content = json.dumps({
                "intent": "GreetingIntent",
                "confidence": 0.99,
                "entities": {}
            })
        elif "2+2" in prompt_lower:
            content = json.dumps({
                "intent": "MathIntent",
                "confidence": 0.98,
                "entities": {"expression": "2+2"}
            })
        # Tier 2: Parameter Extraction
        elif "remind me in 20 minutes" in prompt_lower:
            content = json.dumps({
                "intent": "CreateReminder",
                "confidence": 0.95,
                "entities": {"time": "20 minutes"}
            })
        elif "call mom tomorrow" in prompt_lower:
            content = json.dumps({
                "intent": "CreateReminder",
                "confidence": 0.96,
                "entities": {"time": "tomorrow", "person": "mom"}
            })
        # Tier 3: Ambiguity
        elif "remind me later" in prompt_lower:
            content = json.dumps({
                "intent": "ClarificationIntent",
                "confidence": 0.85,
                "entities": {"missing_parameter": "time"}
            })
        # Tier 4: Negative/Fallback
        elif "asdfasdf" in prompt_lower:
            content = json.dumps({
                "intent": "UnknownIntent",
                "confidence": 0.10,
                "entities": {}
            })
        else:
            # Default fallback
            content = json.dumps({
                "intent": "UnknownIntent",
                "confidence": 0.05,
                "entities": {}
            })
            
        return InferenceResponse(
            content=content,
            model_used="mock-llm-1.0",
            latency_ms=12.0
        )
