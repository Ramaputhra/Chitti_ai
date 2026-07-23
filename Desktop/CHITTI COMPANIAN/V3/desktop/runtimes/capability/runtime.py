import logging
import asyncio
from typing import Any
from desktop.runtimes.workflow.models import ExecutionResult, ExecutionStatus
from desktop.services.language.capability_resolver import CapabilityResolver
from desktop.platform.shared.models.intent import Intent

logger = logging.getLogger(__name__)

class CapabilityRuntime:
    """
    Executes a single capability invocation.
    (Rule 42: Capability Purity)
    Returns exactly one ExecutionResult.
    """
    def __init__(self, resolver: CapabilityResolver, event_bus: Any = None):
        self.resolver = resolver
        self.event_bus = event_bus
        if hasattr(self.event_bus, "subscribe"):
            self.event_bus.subscribe("ToolCallProposed", self._on_tool_call_proposed)
            self.event_bus.subscribe("INTENT_GENERATED", self._on_intent_generated)
            
    def _on_intent_generated(self, event_data: Any):
        payload = getattr(event_data, "payload", event_data.get("payload", {}) if isinstance(event_data, dict) else {})
        intent_event = payload.get("event")
        if not intent_event or not hasattr(intent_event, "desktop_intent"):
            return
            
        desktop_intent = intent_event.desktop_intent
        
        # Translate DesktopIntent to ToolCall
        tool = None
        arguments = {}
        
        if desktop_intent.action.name == "OPEN":
            tool = "application.launch"
            arguments["application"] = desktop_intent.target
            
        if tool:
            logger.info(f"CapabilityRuntime translated local intent to ToolCallProposed: {tool}")
            self._execute_tool(tool, arguments, desktop_intent.session_id)

    def _on_tool_call_proposed(self, event_data: Any):
        payload = getattr(event_data, "payload", event_data.get("payload", {}) if isinstance(event_data, dict) else {})
        tool = payload.get("tool")
        arguments = payload.get("arguments", {})
        session_id = payload.get("session_id", "default")
        
        logger.info(f"CapabilityRuntime processing ToolCallProposed: {tool}")
        self._execute_tool(tool, arguments, session_id)
        
    def _execute_tool(self, tool: str, arguments: dict, session_id: str):
        # We need an async wrapper since invoke is async
        def _invoke_and_publish():
            import asyncio
            
            class DummyToken:
                is_cancelled = False
                
            # Create an event loop for this background thread if needed, or just run it sync
            # Since _run_skill inside invoke uses to_thread, we can just run it synchronously here 
            # for this event handler which is likely running in a background thread anyway.
            # Let's simplify and just do the resolution and execution synchronously for the event handler.
            
            resolve = self.resolver.resolve(tool)
            if not resolve.can_handle or not resolve.skill:
                result = ExecutionResult(
                    status=ExecutionStatus.FAILURE,
                    error_message=f"No capability found for {tool}"
                )
            else:
                intent = Intent(type=tool, confidence=1.0, parameters=arguments)
                try:
                    result = resolve.skill.execute(intent)
                    # Support legacy skills that return None
                    if result is None:
                        result = ExecutionResult(status=ExecutionStatus.SUCCESS)
                except Exception as e:
                    logger.exception(f"Skill execution failed for {tool}")
                    result = ExecutionResult(status=ExecutionStatus.FAILURE, error_message=str(e))
                    
            if hasattr(self.event_bus, "publish"):
                # Wait, ExecutionResultEvent doesn't exist yet, we will define CapabilityExecuted
                from desktop.runtimes.capability.events import CapabilityExecuted
                self.event_bus.publish(CapabilityExecuted(
                    tool=tool,
                    status=result.status.name,
                    error_message=result.error_message,
                    metadata=result.metadata,
                    session_id=session_id
                ))
                
        import threading
        threading.Thread(target=_invoke_and_publish, daemon=True).start()
        
    async def invoke(
        self,
        capability_id: str,
        parameters: dict,
        execution_context: Any,
        cancellation_token: Any
    ) -> ExecutionResult:
        
        resolve = self.resolver.resolve(capability_id)
        if not resolve.can_handle or not resolve.skill:
            return ExecutionResult(
                status=ExecutionStatus.FAILURE, 
                error_message=f"No capability found for {capability_id}"
            )
            
        intent = Intent(type=capability_id, confidence=1.0, parameters=parameters)
        
        # We pass the CancellationToken to allow cooperative cancellation
        # Since skills are currently synchronous, we run them in a thread.
        # Once skills become async, we would await them directly.
        def _run_skill():
            try:
                # Mock cooperative cancellation checking for legacy skills
                if cancellation_token.is_cancelled:
                    return ExecutionResult(status=ExecutionStatus.CANCELLED)
                    
                # In the future, skills will accept (parameters, execution_context, cancellation_token)
                result = resolve.skill.execute(intent)
                if result is None:
                    return ExecutionResult(status=ExecutionStatus.SUCCESS)
                return result
            except Exception as e:
                logger.exception("Skill execution failed")
                return ExecutionResult(status=ExecutionStatus.FAILURE, error_message=str(e))
                
        return await asyncio.to_thread(_run_skill)
