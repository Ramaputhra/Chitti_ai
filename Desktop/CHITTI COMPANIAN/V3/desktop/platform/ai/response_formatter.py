import logging
from typing import Any
from desktop.runtimes.workflow.models import ExecutionStatus

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """
    Subscribes to CapabilityExecuted events and formulates spoken feedback.
    Rule 98 - Capability Contracts: Capabilities communicate exclusively through 
    ExecutionResult. This component turns that result into natural language.
    """
    def __init__(self, event_bus: Any):
        self.event_bus = event_bus
        if hasattr(self.event_bus, "subscribe"):
            self.event_bus.subscribe("CapabilityExecuted", self._on_capability_executed)
            
    def _on_capability_executed(self, event_data: Any):
        payload = getattr(event_data, "payload", event_data.get("payload", {}) if isinstance(event_data, dict) else {})
        tool = payload.get("tool")
        status = payload.get("status")
        error_message = payload.get("error_message")
        metadata = payload.get("metadata", {})
        
        response_text = ""
        
        if tool == "application.launch":
            app_name = metadata.get("application", "the application")
            if status == "SUCCESS":
                response_text = f"Opening {app_name}."
            else:
                response_text = f"I couldn't find {app_name} on this computer."
        else:
            if status == "SUCCESS":
                response_text = "Done."
            else:
                response_text = "I encountered an error."
                
        if response_text and hasattr(self.event_bus, "publish"):
            from desktop.runtimes.expression.outputs.voice.events import SpeakRequested
            logger.info(f"ResponseFormatter generated: {response_text}")
            self.event_bus.publish(SpeakRequested(text=response_text))
