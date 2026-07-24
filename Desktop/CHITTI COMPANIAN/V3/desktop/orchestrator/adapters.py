from desktop.models.experience import Experience
from desktop.brain.execution.models import ExecutionResult
from datetime import datetime

class InputAdapter:
    def translate(self, user_request: str, screen_context: dict, vision_context: dict) -> Experience:
        return Experience(
            experience_id="exp_" + str(hash(user_request))[:8],
            artifact_id="art_" + str(hash(user_request))[:8],
            artifact_type="Experience",
            capability_id="InputAdapter",
            timestamp=None,
            summary=user_request,
            structured_result={"screen": screen_context, "vision": vision_context},
            referenced_entities=[],
            supported_followup_actions=[],
            presentation_available=True,
            expiration_policy="",
            confidence=1.0,
            schema_version="1.0.0",
            experience_type="USER_REQUEST",
            goal=user_request,
            outcome="ACTIVE",
            status="ACTIVE",
            start_time=datetime.now(),
            end_time=datetime.now(),
            decisions=[],
            participants=None,  # Simplified - would need proper participant data
            evidence=None,  # Simplified - would need proper evidence data
            environment=None,  # Simplified - would need proper environment data
            scoring=None,  # Simplified - would need proper scoring data
            continuation_candidate=False,
            fingerprint=str(hash(user_request))
        )

class OutputAdapter:
    def translate(self, result: ExecutionResult) -> dict:
        provenance = []
        for step in result.step_results:
            if hasattr(step, "metadata") and step.metadata:
                provenance.append(step.metadata)
                
        return {
            "ui_signals": {"status": result.overall_status, "confidence": result.execution_confidence},
            "tts_commands": [step.stdout for step in result.step_results if step.stdout],
            "character_signals": {"animation": "success" if result.overall_status == "COMPLETED" else "error"},
            "provenance": provenance
        }
