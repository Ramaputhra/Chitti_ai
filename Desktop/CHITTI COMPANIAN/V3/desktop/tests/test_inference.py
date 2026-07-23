import asyncio
from desktop.app.inference_manager import InferenceManager
from desktop.app.inference_validator import InferenceValidator
from desktop.models.inference import InferenceRequest, InferenceResponse, ProviderHealth
from desktop.platform.inference.inference.mock_llm import MockLLMProvider
from desktop.platform.inference.inference.ollama_provider import OllamaProvider

class BrokenMockProvider(MockLLMProvider):
    def health(self) -> ProviderHealth:
        return ProviderHealth.READY

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        # Returns malformed JSON
        return InferenceResponse(
            content='{ "intent": "broken,',
            model_used="broken-mock",
            latency_ms=5.0
        )

class OverconfidentMockProvider(MockLLMProvider):
    def health(self) -> ProviderHealth:
        return ProviderHealth.READY

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        # Returns confidence 1.7
        return InferenceResponse(
            content='{"intent": "GreetingIntent", "confidence": 1.7}',
            model_used="overconfident-mock",
            latency_ms=5.0
        )

async def run_tests():
    print("--- Running Inference Integration Tests (Sprint 84) ---\n")
    
    validator = InferenceValidator()
    
    # Scenario 1: Mock Provider passes
    print("[Test 1] Standard Mock Provider")
    manager1 = InferenceManager()
    manager1.register(MockLLMProvider())
    resp1 = await manager1.generate(InferenceRequest(prompt="Hello"))
    res1 = validator.validate(resp1)
    assert res1.intent == "GreetingIntent"
    print("✅ Passed")

    # Scenario 2: Malformed JSON -> UnknownIntent
    print("\n[Test 2] Malformed JSON")
    manager2 = InferenceManager()
    manager2.register(BrokenMockProvider())
    resp2 = await manager2.generate(InferenceRequest(prompt="Hello"))
    res2 = validator.validate(resp2)
    assert res2.intent == "UnknownIntent"
    print("✅ Passed (Shielded from JSON Error)")

    # Scenario 3: Confidence clamped
    print("\n[Test 3] Overconfident Clamp")
    manager3 = InferenceManager()
    manager3.register(OverconfidentMockProvider())
    resp3 = await manager3.generate(InferenceRequest(prompt="Hello"))
    res3 = validator.validate(resp3)
    assert res3.confidence == 1.0
    print("✅ Passed (Confidence clamped to 1.0)")

    # Scenario 4: Ollama Unavailable -> Fallback
    print("\n[Test 4] Offline Provider Fallback")
    manager4 = InferenceManager()
    # Assume 127.0.0.1:9999 is offline
    manager4.register(OllamaProvider(host="http://127.0.0.1:9999"))
    resp4 = await manager4.generate(InferenceRequest(prompt="Hello"))
    res4 = validator.validate(resp4)
    assert res4.intent == "UnknownIntent"
    print("✅ Passed (Graceful skip when provider unavailable)")
    
    print("\n✅ All Inference Tests Passed.")

if __name__ == "__main__":
    asyncio.run(run_tests())
