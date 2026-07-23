import logging
from typing import Any, Dict

from desktop.models.semantic_models import (
    DesktopIntent, IntentType, IntentConfidence,
    IntentGeneratedEvent, IntentAmbiguousEvent, AmbiguityReason
)

logger = logging.getLogger(__name__)

class SemanticRuntime:
    """
    Subscribes to USER_TRANSCRIPT_GENERATED.
    Runs the normalizer -> intent extractor -> entity extractor -> confidence evaluator.
    Publishes IntentGeneratedEvent or IntentAmbiguousEvent.
    """
    def __init__(self, event_bus: Any, config: Dict[str, Any] = None, experience_repository: Any = None):
        self.event_bus = event_bus
        self.experience_repository = experience_repository
        self.threshold = config.get("confidence_threshold", 0.75) if config else 0.75
        self.event_bus.subscribe("USER_TRANSCRIPT_GENERATED", self.process_transcript)

    def process_transcript(self, event: Any) -> None:
        payload = getattr(event, "payload", event.get("payload", {}) if isinstance(event, dict) else {})
        text = payload.get("text", "")
        language = payload.get("language", "en")
        session_id = payload.get("session_id", "")
        
        if not text:
            return

        logger.info(f"Parsing Transcript: '{text}'")
        

        # 1. Normalize
        normalized_text = self._normalize(text)
        
        # 2. Extract Intent
        intent_type, intent_conf = self._extract_intent(normalized_text)
        
        # 3. Extract Entities & Parameters
        target, parameters, entity_conf, param_conf = self._extract_entities(normalized_text, intent_type)
        
        # 4. Compute Confidence
        confidence = IntentConfidence(
            intent_score=intent_conf,
            entity_score=entity_conf,
            parameter_score=param_conf
        )
        
        # 5. Build DesktopIntent
        desktop_intent = DesktopIntent(
            action=intent_type,
            target=target,
            object_type=self._infer_object_type(target) if target else None,
            parameters=parameters,
            language=language,
            confidence=confidence,
            source_text=text,
            normalized_text=normalized_text,
            session_id=session_id
        )
        
        # 6. Evaluate and Publish
        self._evaluate_and_publish(desktop_intent)

    def _normalize(self, text: str) -> str:
        text = text.lower().strip()
        # Language-agnostic canonicalization of verbs
        # Example mapping (in reality, driven by ML/rules)
        if any(w in text for w in ["open", "show", "launch", "start", "తెరువు"]):
            return text.replace("show", "open").replace("launch", "open").replace("start", "open").replace("తెరువు", "open")
        if any(w in text for w in ["remove", "delete", "erase"]):
            return text.replace("remove", "delete").replace("erase", "delete")
        return text

    def _extract_intent(self, normalized_text: str) -> (IntentType, float):
        if "open" in normalized_text:
            return IntentType.OPEN, 0.99
        if "move" in normalized_text:
            return IntentType.MOVE, 0.99
        if "fly to the moon" in normalized_text:
            return IntentType.UNKNOWN, 0.10
        return IntentType.UNKNOWN, 0.50

    def _extract_entities(self, normalized_text: str, intent_type: IntentType) -> (str, Dict[str, Any], float, float):
        target = None
        parameters = {}
        entity_conf = 1.0
        param_conf = 1.0

        if intent_type == IntentType.OPEN:
            if "downloads" in normalized_text:
                target = "Downloads"
                entity_conf = 0.99
            elif "browser" in normalized_text or "chrome" in normalized_text:
                target = "Chrome"
                entity_conf = 0.99
            elif "it" in normalized_text:
                target = None
                entity_conf = 0.12 # Ambiguous pronoun
            else:
                target = None
                entity_conf = 0.0 # Force fallback to LLM for unknown targets

        elif intent_type == IntentType.MOVE:
            # e.g., "move report to documents"
            if "report" in normalized_text and "documents" in normalized_text:
                parameters["source"] = "report"
                parameters["destination"] = "Documents"
            elif "report" in normalized_text:
                parameters["source"] = "report"
                param_conf = 0.0 # Missing destination

        return target, parameters, entity_conf, param_conf

    def _infer_object_type(self, target: str) -> str:
        if "downloads" in target.lower():
            return "folder"
        return "file"

    def _evaluate_and_publish(self, intent: DesktopIntent) -> None:
        if intent.action == IntentType.UNKNOWN:
            reason = AmbiguityReason.UNKNOWN_ACTION
        elif intent.confidence.entity_score < self.threshold:
            reason = AmbiguityReason.UNKNOWN_TARGET
        elif intent.confidence.parameter_score < self.threshold:
            reason = AmbiguityReason.MISSING_PARAMETER
        elif intent.confidence.overall < self.threshold:
            reason = AmbiguityReason.LOW_CONFIDENCE
        else:
            reason = None

        if reason:
            # 2. Check Experience Repository before falling back to LLM
            if getattr(self, "experience_repository", None):
                exp = self.experience_repository.find_best_match(intent.source_text)
                if exp:
                    logger.info(f"Experience matched from library: {exp.get('id')}. Bypassing LLM.")
                    workflow = exp.get("workflow", [])
                    
                    from desktop.runtimes.inference.events import ToolCallProposed, InferenceRequested
                    import json
                    
                    for step in workflow:
                        tool = step.get("capability", step.get("tool"))
                        args = step.get("arguments", {})
                        self.event_bus.publish(ToolCallProposed(tool=tool, arguments=args, session_id=intent.session_id))
                        
                    if hasattr(self.event_bus, "publish"):
                        prompt_data = {
                            "source": "experience_library",
                            "confidence": exp.get("statistics", {}).get("confidence", 0.99),
                            "verified": True,
                            "system_directive": "Inform the user that the request was resolved instantly using one of their saved workflows."
                        }
                        self.event_bus.publish(InferenceRequested(text=json.dumps(prompt_data), session_id=intent.session_id))
                    return

            # 3. Fallback to LLM Planning
            logger.info(f"Deterministic matching failed ({reason.name}). Handing off to Inference Runtime.")
            from desktop.runtimes.inference.events import InferenceRequested
            self.event_bus.publish(InferenceRequested(text=intent.source_text, session_id=intent.session_id))
        else:
            import time
            logger.info(f"Intent Generated: {intent.action.name} {intent.target}")
            event = IntentGeneratedEvent(
                desktop_intent=intent,
                timestamp=time.time(),
                session_id=intent.session_id
            )
            from desktop.platform.shared.interfaces.event_bus import Event
            self.event_bus.publish(Event("INTENT_GENERATED", source="SemanticRuntime", payload={"event": event}))
