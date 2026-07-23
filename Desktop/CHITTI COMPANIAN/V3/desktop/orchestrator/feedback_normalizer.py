import uuid
import time
from typing import Dict, Any

class FeedbackClassification:
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILURE = "FAILURE"
    USER_CANCELLED = "USER_CANCELLED"
    ROLLBACK_SUCCESS = "ROLLBACK_SUCCESS"
    ROLLBACK_FAILURE = "ROLLBACK_FAILURE"
    TIMEOUT = "TIMEOUT"

class FeedbackNormalizer:
    @staticmethod
    def classify(step_result: Any) -> str:
        status = getattr(step_result, "status", None)
        if status == "COMPLETED":
            return FeedbackClassification.SUCCESS
        elif status == "FAILED":
            metadata = getattr(step_result, "metadata", {})
            if metadata.get("rollback_performed", False):
                return FeedbackClassification.ROLLBACK_SUCCESS
            return FeedbackClassification.FAILURE
        return FeedbackClassification.FAILURE

    @staticmethod
    def normalize(step_result: Any, correlation_id: str) -> Dict[str, Any]:
        classification = FeedbackNormalizer.classify(step_result)
        metadata = getattr(step_result, "metadata", {})
        
        semantic_text = f"System Action: {getattr(step_result, 'intent', 'unknown')} "
        semantic_text += f"Outcome: {classification}. "
        semantic_text += f"Details: {getattr(step_result, 'stdout', '')}."
        
        return {
            "feedback_id": "fb_" + str(uuid.uuid4())[:8],
            "originating_execution_id": getattr(step_result, "step_id", ""),
            "originating_pipeline_correlation_id": correlation_id,
            "classification": classification,
            "semantic_text": semantic_text,
            "timestamp": time.time(),
            "metadata": metadata
        }
