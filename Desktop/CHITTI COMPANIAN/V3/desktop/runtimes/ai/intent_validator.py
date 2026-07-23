import json
import logging
from typing import Dict, Any, Optional
from desktop.models.interaction import IntentResult

logger = logging.getLogger(__name__)

class IntentValidator:
    """
    Validates JSON output from InferenceRuntime to ensure it matches
    the allowed schema before passing it to PlannerRuntime.
    """
    
    ALLOWED_INTENTS = {
        "LaunchAppIntent",
        "CloseAppIntent",
        "ResumeActivityIntent",
        "OpenBrowserIntent",
        "ClarificationIntent",
        "DistanceIntent",
        "ShowMeIntent",
        "SystemCommand",
        "StateQueryIntent",
        "CommandIntent",
        "QuestionIntent",
        "ReasoningIntent",
        "SummarizationIntent",
        "WritingIntent",
        "TranslationIntent",
        "CreativeIntent",
        "SmallTalkIntent"
    }

    @staticmethod
    def validate(raw_json: str, interaction_id: str, source: str, original_text: str = "") -> Optional[IntentResult]:
        try:
            import re
            
            # JSON Syntax Validation - Robust Markdown Stripping
            clean_json = raw_json.strip()
            
            # Find the first { and last } to robustly extract JSON from markdown/text
            start_idx = clean_json.find('{')
            end_idx = clean_json.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                clean_json = clean_json[start_idx:end_idx+1]
                
            data = json.loads(clean_json)
            
            intent_type = data.get("intent")
            parameters = data.get("parameters", {})
            
            # Intent Type Validation
            if intent_type not in IntentValidator.ALLOWED_INTENTS:
                logger.warning(f"Invalid intent type received: {intent_type}")
                return IntentValidator._fallback(interaction_id, source)
                
            # Intent Normalization & Semantic Consistency
            original_lower = original_text.lower().strip()
            greetings = {"hi", "hello", "hai", "hey", "good morning", "good evening"}
            if original_lower in greetings:
                intent_type = "SmallTalkIntent"
                parameters = {}

            # Required Parameter Validation & Clarification Generation
            executable_requirements = {
                "LaunchAppIntent": ["app_command"],
                "CloseAppIntent": ["app_command"],
                "DistanceIntent": ["destination"],
            }

            if intent_type in executable_requirements:
                missing = []
                for req in executable_requirements[intent_type]:
                    val = parameters.get(req, "")
                    if not val or str(val).strip() == "":
                        missing.append(req)
                
                if missing:
                    logger.warning(f"Missing mandatory parameter {missing[0]} for {intent_type}. Converting to ClarificationIntent.")
                    return IntentResult(
                        intent="ClarificationIntent",
                        confidence=1.0,
                        parameters={"reason": f"missing_parameter: {missing[0]}"},
                        source=source,
                        interaction_id=interaction_id,
                        model="validator_fallback"
                    )

            return IntentResult(
                intent=intent_type,
                confidence=float(data.get("confidence", 0.9)),
                parameters=parameters,
                source=source,
                interaction_id=interaction_id,
                model="qwen2.5-1.5b-instruct"
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM: {e}\nRaw: {raw_json}")
            return IntentValidator._fallback(interaction_id, source)
        except Exception as e:
            logger.error(f"Intent validation error: {e}")
            return IntentValidator._fallback(interaction_id, source)
            
    @staticmethod
    def _fallback(interaction_id: str, source: str) -> IntentResult:
        return IntentResult(
            intent="ClarificationIntent",
            confidence=1.0,
            parameters={"reason": "parsing_failed"},
            source=source,
            interaction_id=interaction_id,
            model="system_fallback"
        )
