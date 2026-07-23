import logging
from typing import Any, Dict

from desktop.models.presentation_models import ResponseIntent, ResponseCreatedEvent

logger = logging.getLogger(__name__)

class ResponseBuilder:
    """
    Deterministic builder. Converts a verified execution status into a structured ResponseIntent.
    No personality or text generation happens here.
    """
    def __init__(self, event_bus: Any):
        self.event_bus = event_bus

    def build_response(self, workflow_id: str, capability_id: str, status: str, parameters: Dict[str, Any]) -> ResponseIntent:
        logger.info(f"ResponseBuilder: Generating ResponseIntent for {capability_id} ({status})")
        
        # Simple deterministic mapping
        if capability_id == "sys.folder.open":
            if status == "SUCCESS":
                intent = ResponseIntent(
                    status="SUCCESS",
                    message_key="folder.opened",
                    context={"folder_path": parameters.get("folder_path", "unknown")}
                )
            else:
                intent = ResponseIntent(
                    status="FAILED",
                    message_key="folder.open_failed",
                    context={"folder_path": parameters.get("folder_path", "unknown")}
                )
        else:
            intent = ResponseIntent(
                status=status,
                message_key="unknown.completed",
                context={}
            )
            
        import time
        event = ResponseCreatedEvent(workflow_id=workflow_id, response_intent=intent, timestamp=time.time())
        self.event_bus.publish("RESPONSE_CREATED", source="ResponseBuilder", payload={"event": event})
        
        return intent
