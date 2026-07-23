import logging
from typing import Dict, Any, Optional

from desktop.models.ai_result import AIResult
from desktop.models.ai_payloads import IntentClassification
from desktop.infrastructure.database.experience_db import ExperienceDatabase
from desktop.platform.capabilities.registry import capability_registry

logger = logging.getLogger(__name__)

class ExperienceResolver:
    """
    Sub-component of the Learning Engine.
    Handles the Exact -> Pattern -> Semantic resolution strategy.
    """
    def __init__(self, db: ExperienceDatabase):
        self.db = db
        
    def resolve(self, command: str, intent_result: AIResult[IntentClassification]) -> Optional[Dict[str, Any]]:
        """
        Attempts to resolve the command to a historical experience.
        Returns the resolved experience dictionary if found.
        """
        # 1. Exact Match
        exact_match = self.db.find_exact_match(command)
        if exact_match:
            logger.info(f"ExperienceResolver: Exact Match found for '{command}'")
            return exact_match
            
        # 2. Pattern Match
        pattern_match = self.db.find_pattern_match(command)
        if pattern_match:
            logger.info(f"ExperienceResolver: Pattern Match found for '{command}'")
            return pattern_match
            
        # 3. Semantic Match (Future BGE integration)
        return None


class ExperienceLearningEngine:
    """
    The centerpiece of CHITTI's intelligence.
    Sits between Intent generation and physical Capability execution.
    It accumulates, refines, reuses, and generalizes successful experiences.
    """
    def __init__(self, db: ExperienceDatabase):
        self.db = db
        self.resolver = ExperienceResolver(db)
        
    def process_and_execute(self, command: str, intent_result: AIResult[IntentClassification], 
                            runtime_context: Dict[str, Any]) -> bool:
        """
        Takes the raw intent from the IntentService, resolves it against historical experience,
        computes final confidence, and delegates to execution.
        """
        # 1. Resolve against past experience
        experience = self.resolver.resolve(command, intent_result)
        
        final_intent = intent_result.payload.intent
        capability_id = None
        parameters = intent_result.payload.entities
        
        # 2. Confidence Evolution Scoring
        if experience:
            # We found a historical success. Boost confidence.
            hist_success_rate = experience.get('success_rate', 0.0)
            base_confidence = intent_result.confidence
            final_confidence = (base_confidence + hist_success_rate + 1.0) / 3.0 # Simple heuristic boost
            
            final_intent = experience['intent']
            capability_id = experience['capability_id']
            # We could overlay parameters here
            
            logger.info(f"Experience Boost: Confidence elevated from {base_confidence:.2f} to {final_confidence:.2f}")
        else:
            final_confidence = intent_result.confidence
            
            # If no historical experience, we map the intent to capability ID normally
            # For this demo, we assume the intent name maps 1:1 to registry name (e.g., OPEN_FOLDER)
            capability_id = final_intent
            
        # 3. Execution Thresholds
        if final_confidence >= 0.95:
            return self._execute_and_verify(command, final_intent, capability_id, parameters, final_confidence, runtime_context)
        elif final_confidence >= 0.75:
            logger.warning(f"Confidence {final_confidence:.2f} requires verification. (Stubbed: Assuming user verified).")
            return self._execute_and_verify(command, final_intent, capability_id, parameters, final_confidence, runtime_context)
        else:
            logger.warning("Confidence too low. Delegating to Reasoning LLM (Gemma/Qwen).")
            return False

    def _execute_and_verify(self, command: str, intent: str, capability_id: str, 
                            parameters: Dict[str, Any], confidence: float, context: Dict[str, Any]) -> bool:
        """Executes the capability and logs the experience if successful (not corrected by user)."""
        import time
        start_time = time.perf_counter()
        
        success = capability_registry.execute(capability_id, **parameters)
        execution_time_ms = int((time.perf_counter() - start_time) * 1000)
        
        if success:
            # Simulated verification step (Assume user didn't correct it within a short window)
            user_verified = True 
            
            if user_verified:
                exp_id = self.db.save_experience(
                    command=command,
                    intent=intent,
                    capability=capability_id,
                    parameters=parameters,
                    context=context,
                    confidence=confidence,
                    execution_time=execution_time_ms
                )
                logger.info(f"Experience Learned & Saved! (Experience ID: {exp_id})")
                
        return success
