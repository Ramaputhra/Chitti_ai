from desktop.models.experience import Experience
from desktop.brain.execution.models import ExecutionResult

class InputAdapter:
    def translate(self, user_request: str, screen_context: dict, vision_context: dict) -> Experience:
        return Experience(
            experience_id="exp_" + str(hash(user_request))[:8],
            raw_input=user_request,
            context={"screen": screen_context, "vision": vision_context},
            timestamp=0.0
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
