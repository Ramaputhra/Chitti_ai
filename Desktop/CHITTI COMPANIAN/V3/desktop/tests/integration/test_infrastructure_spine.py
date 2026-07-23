import unittest
import os
import tempfile
import yaml
from typing import Any

from desktop.models.component_states import HealthState, LifecycleState
from desktop.models.ai_context import RuntimeContext
from desktop.models.ai_result import AIResult, InferenceMetadata
from desktop.models.ai_payloads import IntentClassification
from desktop.models.component_manifest import ComponentManifest, CapabilityRequirements

from desktop.platform.components.adapter import ProviderAdapter
from desktop.platform.components.loader import ManifestLoader
from desktop.platform.components.registry import ProviderRegistry
from desktop.runtimes.component_runtime import ComponentRuntime

# ==========================================
# 1. Mock Providers (Step 1)
# ==========================================

class MockIntentProviderV1(ProviderAdapter):
    def __init__(self):
        self._health = HealthState.UNKNOWN
        
    def initialize(self) -> None:
        self._health = HealthState.AVAILABLE
        
    def health_check(self) -> HealthState:
        return self._health
        
    def warm(self) -> None:
        self._health = HealthState.READY
        
    def execute(self, payload: Any, context: RuntimeContext) -> AIResult[IntentClassification]:
        self._health = HealthState.BUSY
        
        # Validate context is passed properly
        assert context is not None
        assert context.device in ["cpu", "gpu", "npu"]
        
        metadata = InferenceMetadata(
            model_id="mock_intent_v1",
            provider_backend="mock",
            latency_ms=10.0,
            cached=False
        )
        
        result = IntentClassification(
            intent="OPEN_APPLICATION",
            confidence=0.99,
            entities={"app": "chrome"}
        )
        
        self._health = HealthState.READY
        return AIResult(payload=result, confidence=0.99, metadata=metadata)
        
    def unload(self) -> None:
        self._health = HealthState.OFFLINE
        
    # For testing specific failure states
    def set_health(self, state: HealthState):
        self._health = state


class MockIntentProviderV2(MockIntentProviderV1):
    def execute(self, payload: Any, context: RuntimeContext) -> AIResult[IntentClassification]:
        self._health = HealthState.BUSY
        
        metadata = InferenceMetadata(
            model_id="mock_intent_v2",
            provider_backend="mock",
            latency_ms=5.0,
            cached=True
        )
        
        result = IntentClassification(
            intent="CLOSE_APPLICATION",
            confidence=0.95,
            entities={"app": "chrome"}
        )
        
        self._health = HealthState.READY
        return AIResult(payload=result, confidence=0.95, metadata=metadata)


# ==========================================
# AI Runtime & Service (Step 4 & 5)
# ==========================================

class IntentRuntime:
    def __init__(self, component_runtime: ComponentRuntime):
        self.component_runtime = component_runtime
        
    def classify(self, text: str, context: RuntimeContext) -> AIResult[IntentClassification]:
        manifests = self.component_runtime.registry.find_by_capability("intent_classification")
        if not manifests:
            raise RuntimeError("Missing Component: No provider supports intent_classification")
            
        component_id = manifests[0].component_id
        
        health = self.component_runtime.check_health(component_id)
        if health == HealthState.FAILED:
            raise RuntimeError("Unhealthy Provider")
            
        if health == HealthState.BUSY:
            raise RuntimeError("Provider is Busy") # Stub for scheduler queuing
            
        adapter = self.component_runtime.get_adapter(component_id)
        if not adapter:
            raise RuntimeError("Adapter not loaded")
            
        return adapter.execute(text, context)


class IntentService:
    def __init__(self, intent_runtime: IntentRuntime):
        self.intent_runtime = intent_runtime
        
    def classify(self, text: str) -> AIResult[IntentClassification]:
        context = RuntimeContext(device="cpu", priority=0)
        return self.intent_runtime.classify(text, context)


# ==========================================
# Tests
# ==========================================

class TestInfrastructureSpine(unittest.TestCase):
    
    def setUp(self):
        self.loader = ManifestLoader()
        self.registry = ProviderRegistry()
        self.comp_runtime = ComponentRuntime(self.registry, self.loader)
        self.intent_runtime = IntentRuntime(self.comp_runtime)
        self.intent_service = IntentService(self.intent_runtime)
        
        # Create a mock YAML manifest file
        self.test_dir = tempfile.TemporaryDirectory()
        self.manifest_path = os.path.join(self.test_dir.name, "mock_v1.yaml")
        
        manifest_data = {
            "component_id": "mock_intent_v1",
            "component_type": "ai_model",
            "provider_backend": "mock",
            "runtime": "mockruntime",
            "version": "1.0",
            "capabilities": ["intent_classification"]
        }
        with open(self.manifest_path, 'w') as f:
            yaml.dump(manifest_data, f)
            
    def tearDown(self):
        self.test_dir.cleanup()

    def test_01_manifest_loader_and_registry(self):
        # Step 2: Register it
        self.comp_runtime.discover_components(self.test_dir.name)
        
        manifest = self.registry.find_by_id("mock_intent_v1")
        self.assertIsNotNone(manifest)
        self.assertEqual(manifest.component_id, "mock_intent_v1")
        self.assertIn("intent_classification", manifest.capabilities)
        
        # Capability resolution
        providers = self.registry.find_by_capability("intent_classification")
        self.assertEqual(len(providers), 1)

    def test_02_component_runtime_validation(self):
        # Step 3: Lifecycle and Health transitions
        self.comp_runtime.discover_components(self.test_dir.name)
        
        # Before load, health should be OFFLINE since manifest exists but adapter doesn't
        self.assertEqual(self.comp_runtime.check_health("mock_intent_v1"), HealthState.OFFLINE)
        
        adapter = MockIntentProviderV1()
        success = self.comp_runtime.load_component("mock_intent_v1", adapter)
        self.assertTrue(success)
        
        # After initialize
        self.assertEqual(self.comp_runtime.check_health("mock_intent_v1"), HealthState.AVAILABLE)
        
        # Warm up
        self.comp_runtime.warm_component("mock_intent_v1")
        self.assertEqual(self.comp_runtime.check_health("mock_intent_v1"), HealthState.READY)
        
        # Unload
        self.comp_runtime.unload_component("mock_intent_v1")
        self.assertEqual(self.comp_runtime.check_health("mock_intent_v1"), HealthState.OFFLINE)

    def test_03_missing_component(self):
        # Do not discover/register anything
        with self.assertRaisesRegex(RuntimeError, "Missing Component"):
            self.intent_service.classify("open chrome")

    def test_04_wrong_capability(self):
        self.comp_runtime.discover_components(self.test_dir.name)
        providers = self.registry.find_by_capability("semantic_search")
        self.assertEqual(len(providers), 0)

    def test_05_unhealthy_provider(self):
        self.comp_runtime.discover_components(self.test_dir.name)
        adapter = MockIntentProviderV1()
        self.comp_runtime.load_component("mock_intent_v1", adapter)
        
        adapter.set_health(HealthState.FAILED)
        
        with self.assertRaisesRegex(RuntimeError, "Unhealthy Provider"):
            self.intent_service.classify("open chrome")

    def test_06_busy_provider(self):
        self.comp_runtime.discover_components(self.test_dir.name)
        adapter = MockIntentProviderV1()
        self.comp_runtime.load_component("mock_intent_v1", adapter)
        
        adapter.set_health(HealthState.BUSY)
        
        with self.assertRaisesRegex(RuntimeError, "Provider is Busy"):
            self.intent_service.classify("open chrome")

    def test_07_end_to_end_runtime_context(self):
        # Step 4 & 5: AI Runtime & Service End to End
        self.comp_runtime.discover_components(self.test_dir.name)
        adapter = MockIntentProviderV1()
        self.comp_runtime.load_component("mock_intent_v1", adapter)
        
        result = self.intent_service.classify("open chrome")
        
        # Verify typed payload and metadata
        self.assertIsInstance(result, AIResult)
        self.assertIsInstance(result.payload, IntentClassification)
        self.assertEqual(result.payload.intent, "OPEN_APPLICATION")
        self.assertEqual(result.metadata.model_id, "mock_intent_v1")
        
    def test_08_provider_interchangeability(self):
        # Register V1
        self.comp_runtime.discover_components(self.test_dir.name)
        
        # Load V1
        adapter_v1 = MockIntentProviderV1()
        self.comp_runtime.load_component("mock_intent_v1", adapter_v1)
        
        res1 = self.intent_service.classify("test")
        self.assertEqual(res1.payload.intent, "OPEN_APPLICATION")
        
        # Unload V1, replace with V2 adapter without changing AI Runtime or Service
        self.comp_runtime.unload_component("mock_intent_v1")
        adapter_v2 = MockIntentProviderV2()
        self.comp_runtime.load_component("mock_intent_v1", adapter_v2) # Swapped
        
        res2 = self.intent_service.classify("test")
        self.assertEqual(res2.payload.intent, "CLOSE_APPLICATION")
        self.assertEqual(res2.metadata.model_id, "mock_intent_v2")


if __name__ == "__main__":
    unittest.main()
