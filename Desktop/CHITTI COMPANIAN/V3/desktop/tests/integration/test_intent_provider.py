import unittest
import os
import tempfile
import yaml
import json
from unittest.mock import patch, MagicMock

from desktop.models.ai_context import RuntimeContext
from desktop.platform.benchmark.tracker import BenchmarkTracker
from desktop.platform.components.loader import ManifestLoader
from desktop.platform.components.registry import ProviderRegistry
from desktop.runtimes.component_runtime import ComponentRuntime
from desktop.platform.components.adapters.text_classification import TextClassificationProvider
from desktop.platform.ai.intent_service import IntentService
from desktop.platform.capabilities.registry import capability_registry
from desktop.capabilities.files import open_folder

class TestIntentProvider(unittest.TestCase):
    def setUp(self):
        # 1. Setup Infrastructure
        self.loader = ManifestLoader()
        self.registry = ProviderRegistry()
        self.comp_runtime = ComponentRuntime(self.registry, self.loader)
        self.tracker = BenchmarkTracker()
        
        # 2. Register Python Capabilities
        capability_registry.register("OPEN_FOLDER", open_folder)
        
        # 3. Create Manifest
        self.test_dir = tempfile.TemporaryDirectory()
        self.manifest_path = os.path.join(self.test_dir.name, "intent_provider.yaml")
        
        manifest_data = {
            "component_id": "chitti_intent_classifier",
            "component_type": "ai_model",
            "provider_backend": "transformers",
            "runtime": "python",
            "version": "1.0",
            "capabilities": ["intent_classification"]
        }
        with open(self.manifest_path, 'w') as f:
            yaml.dump(manifest_data, f)
            
        self.comp_runtime.discover_components(self.test_dir.name)
        
        # 4. Initialize Service
        self.intent_service = IntentService(self.comp_runtime)
        
        # Override dataset path for test
        self.test_dataset = os.path.join(self.test_dir.name, "test_intent_dataset.jsonl")
        self.intent_service.dataset_path = self.test_dataset

    def tearDown(self):
        self.test_dir.cleanup()

    @patch('desktop.platform.components.adapters.text_classification.pipeline')
    def test_end_to_end_capability_demonstration(self, mock_pipeline_builder):
        """
        Demonstrates the exact Capability flow requested:
        User "Open Downloads" -> Intent Provider -> IntentService -> Registry -> Execute -> Log
        """
        # Mock the HuggingFace pipeline to return exactly what XLM-RoBERTa would
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [{'label': 'OPEN_FOLDER', 'score': 0.99}]
        mock_pipeline_builder.return_value = mock_pipeline
        
        # Load the adapter (using XLM-RoBERTa instead of ModernBERT)
        adapter = TextClassificationProvider("xlm-roberta-base", "chitti_intent_classifier", self.tracker)
        self.comp_runtime.load_component("chitti_intent_classifier", adapter)
        self.comp_runtime.warm_component("chitti_intent_classifier")
        
        # Execute the flow
        context = RuntimeContext(priority=1)
        
        # STEP 1: Predict Intent
        result = self.intent_service.classify("Open Downloads", context)
        
        # Verification of AI Model routing
        self.assertEqual(result.payload.intent, "OPEN_FOLDER")
        self.assertEqual(result.confidence, 0.99)
        
        # STEP 2: Confidence > 0.95, so we expect it to be logged for local training
        self.assertTrue(os.path.exists(self.test_dataset))
        with open(self.test_dataset, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            data = json.loads(lines[0])
            self.assertEqual(data["text"], "Open Downloads")
            self.assertEqual(data["intent"], "OPEN_FOLDER")
            
        # STEP 3: Execute the Capability via Registry
        with patch('desktop.capabilities.files.os.startfile') as mock_startfile:
            success = capability_registry.execute(result.payload.intent)
            self.assertTrue(success)
            mock_startfile.assert_called_once_with(os.path.expanduser("~/Downloads"))

    @patch('desktop.platform.components.adapters.text_classification.pipeline')
    def test_confidence_rules_fallback(self, mock_pipeline_builder):
        """Test that confidence < 0.75 triggers fallback warning (no log)."""
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [{'label': 'UNKNOWN', 'score': 0.45}]
        mock_pipeline_builder.return_value = mock_pipeline
        
        adapter = TextClassificationProvider("mock", "chitti_intent_classifier", self.tracker)
        self.comp_runtime.load_component("chitti_intent_classifier", adapter)
        self.comp_runtime.warm_component("chitti_intent_classifier")
        
        result = self.intent_service.classify("Something confusing", RuntimeContext())
        self.assertEqual(result.payload.intent, "UNKNOWN")
        
        # Since confidence is 0.45, it should NOT log to the verified dataset
        self.assertFalse(os.path.exists(self.test_dataset))


if __name__ == "__main__":
    unittest.main()
