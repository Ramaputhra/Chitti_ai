import os
import logging
from desktop.models.ai_context import RuntimeContext
from desktop.models.ai_result import AIResult
from desktop.models.ai_payloads import IntentClassification
from desktop.models.component_states import HealthState
from desktop.runtimes.component_runtime import ComponentRuntime

logger = logging.getLogger(__name__)

class IntentService:
    """
    The semantic orchestrator for Intent Classification.
    Enforces strict Confidence Rules:
    - >= 0.95: Execute immediately
    - 0.75 - 0.94: Local Verification / Disambiguation
    - < 0.75: Fallback to Reasoning Model (Gemma/Qwen)
    """
    def __init__(self, component_runtime: ComponentRuntime):
        self.component_runtime = component_runtime
        
        # Ensure training directory exists
        self.dataset_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            "data", "training", "intent_dataset.jsonl"
        )
        os.makedirs(os.path.dirname(self.dataset_path), exist_ok=True)

    def classify(self, text: str, context: RuntimeContext) -> AIResult[IntentClassification]:
        # 1. Ask registry for a provider supporting 'intent_classification'
        manifests = self.component_runtime.registry.find_by_capability("intent_classification")
        if not manifests:
            raise RuntimeError("No provider found for capability: intent_classification")
            
        # Select the highest priority or first available
        component_id = manifests[0].component_id
        
        # 2. Check health and execute
        health = self.component_runtime.check_health(component_id)
        if health not in [HealthState.READY, HealthState.AVAILABLE]:
            raise RuntimeError(f"Provider {component_id} is unavailable (State: {health})")
            
        adapter = self.component_runtime.get_adapter(component_id)
        
        # Execute the model-agnostic classification
        result: AIResult[IntentClassification] = adapter.execute(text, context)
        confidence = result.confidence
        
        logger.info(f"Classified '{text}' as {result.payload.intent} (Confidence: {confidence:.2f})")
        
        # 3. Confidence Rules Execution
        if confidence >= 0.95:
            # Log to training dataset immediately since it's highly confident
            self._log_verified_intent(text, result.payload.intent)
            return result
        elif confidence >= 0.75:
            logger.warning("Confidence between 0.75-0.94. Local verification needed (stubbed).")
            # Stub: Normally we'd ask the user or check recent context
            return result
        else:
            logger.warning("Confidence < 0.75. Falling back to LLM Reasoning (stubbed).")
            # Stub: Normally we'd route to Gemma/Qwen capability here
            return result

    def _log_verified_intent(self, text: str, intent: str):
        """Append to the local intent dataset for future CHITTI-Intent v1 training."""
        import json
        with open(self.dataset_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"text": text, "intent": intent}) + "\n")
