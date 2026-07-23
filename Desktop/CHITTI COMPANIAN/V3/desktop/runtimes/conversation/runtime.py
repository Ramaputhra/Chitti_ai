import logging
from typing import Any, Dict
from desktop.models.conversation import ConversationSession, EntityDescriptor, ExecutionContext, CompanionContext, ConversationArtifact
from desktop.runtimes.conversation.conversation_resolver import ConversationResolver

logger = logging.getLogger(__name__)

class ConversationRuntime:
    """
    Owns conversational state, entity resolution, and session lifecycle.
    Complies with Rule 246.
    """
    def __init__(self, event_bus: Any, ai_runtime: Any = None):
        self.event_bus = event_bus
        self.ai_runtime = ai_runtime
        self.context = None
        self.sessions: Dict[str, ConversationSession] = {}
        
        if hasattr(self.event_bus, "subscribe"):
            self.event_bus.subscribe("InteractionEnvelope", self._on_interaction)
            self.event_bus.subscribe("CapabilityExecuted", self._on_capability_executed)
            
            from desktop.models.events import ExecutionCompletedEvent
            self.event_bus.subscribe(ExecutionCompletedEvent, self._on_execution_completed)
            
    async def initialize(self, context) -> bool:
        self.context = context
        return True
        
    async def start(self):
        logger.info("ConversationRuntime started.")
        # Reconstruct default session
        self._get_or_create_session("default")
        return True
        
    async def stop(self):
        return True
        
    async def shutdown(self):
        return True
        
    def _get_or_create_session(self, session_id: str) -> ConversationSession:
        if session_id in self.sessions:
            return self.sessions[session_id]
            
        session = ConversationSession(session_id=session_id)
        if self.context:
            from desktop.app.memory_contracts import IMemoryService
            memory_service = self.context.registry.resolve(IMemoryService)
            if memory_service and hasattr(memory_service, "load_recent_history"):
                history = memory_service.load_recent_history(session_id, limit=20)
                session.history = history
                
        self.sessions[session_id] = session
        return session
        
    def _on_interaction(self, event_data: Any):
        """
        Handles incoming InteractionEnvelope from the Transport Layer.
        Implements Split Routing and deterministic Entity Resolution.
        """
        logger.info(f"[ConversationRuntime] Received InteractionEnvelope: {event_data.id}")
        
        if not self.ai_runtime or not self.context:
            logger.warning("Missing dependencies. Cannot resolve intent.")
            return
            
        from desktop.app.memory_contracts import IMemoryService
        memory_service = self.context.registry.resolve(IMemoryService)
        
        # 1. Fetch Session
        session_id = "default"
        session = self._get_or_create_session(session_id)
        
        raw_payload = str(event_data.payload)
        source = event_data.origin
        
        # 2. Entity & Context Resolution
        resolved_interaction = ConversationResolver.resolve(raw_payload, session.focus, session)
        if raw_payload != resolved_interaction.resolved_text:
            logger.info(f"[ConversationRuntime] Context Expanded: '{raw_payload}' -> '{resolved_interaction.resolved_text}'")
            
        # Presentation Routing Interception
        if resolved_interaction.routing_action == "Presentation":
            logger.info(f"[ConversationRuntime] Routing to Presentation Engine for {raw_payload}")
            # Invoke Presentation Engine (mocked via EventBus for now)
            from desktop.models.presentation import RenderedExpression
            from datetime import datetime
            from uuid import uuid4
            if hasattr(self.event_bus, "publish") and session.focus.current_conversation_artifact:
                self.event_bus.publish(RenderedExpression(
                    timestamp=datetime.now(),
                    correlation_id=str(uuid4()),
                    formats={"text": f"Presenting {session.focus.current_conversation_artifact.artifact_type}"}
                ))
            return
        
        # 3. Add to history
        session.history.append({"role": "user", "content": raw_payload})
        if memory_service and hasattr(memory_service, "append_message_to_history"):
            memory_service.append_message_to_history(session_id, "user", raw_payload)
        
        # Populate Summaries for AIRuntime
        resolved_interaction.focus_summary = f"Topic: {session.focus.current_topic}, Last Intent: {session.focus.last_intent}"
        if session.focus.current_conversation_artifact:
            art = session.focus.current_conversation_artifact
            resolved_interaction.artifact_summary = f"Active Artifact: {art.artifact_type} ({art.summary})"
        else:
            resolved_interaction.artifact_summary = "No active artifact."
            
        # 4. Resolve Intent using the full interaction object
        # We attach the event ID so AIRuntime can use it for tracing
        resolved_interaction.id = event_data.id
        intent_result = self.ai_runtime.resolve_intent(
            interaction=resolved_interaction,
            source=source,
            session=session
        )
        
        session.last_intent = intent_result.intent
        if hasattr(intent_result, "parameters") and intent_result.parameters:
            session.last_entities = intent_result.parameters
            # Add to recent entities
            if intent_result.intent == "LaunchAppIntent" and "app_command" in intent_result.parameters:
                app_name = intent_result.parameters["app_command"]
                session.recent_entities.append(EntityDescriptor(id=f"app_{app_name}", display=app_name, type="application", executable=app_name))
        
        # 5. Split Routing
        CONVERSATION_INTENTS = {
            "SmallTalkIntent", 
            "ClarificationIntent", 
            "ReasoningIntent", 
            "SummarizationIntent", 
            "WritingIntent", 
            "TranslationIntent", 
            "CreativeIntent",
            "QuestionIntent"
        }
        
        is_conversation = intent_result.intent in CONVERSATION_INTENTS
            
        if is_conversation or intent_result.confidence < 0.5:
            # Bypass planner, handle conversationally
            response_text = self.ai_runtime.generate_response(session, intent_result.intent)
            
            session.history.append({"role": "assistant", "content": response_text})
            if memory_service and hasattr(memory_service, "append_message_to_history"):
                memory_service.append_message_to_history(session_id, "assistant", response_text)
            
            from desktop.models.presentation import RenderedExpression
            from datetime import datetime
            from uuid import uuid4
            if hasattr(self.event_bus, "publish"):
                self.event_bus.publish(RenderedExpression(
                    timestamp=datetime.now(),
                    correlation_id=str(uuid4()),
                    formats={"text": response_text}
                ))
        else:
            # Action Intent -> Send to Planner
            from desktop.models.interaction import IntentResolved
            resolved_event = IntentResolved(
                timestamp=event_data.timestamp,
                source="ConversationRuntime",
                correlation_id=event_data.correlation_id,
                event_type="INTENT_RESOLVED",
                result=intent_result
            )
            if hasattr(self.event_bus, "publish"):
                self.event_bus.publish(resolved_event)
        
    def _on_capability_executed(self, event_data: Any):
        """Update ExecutionContext in session"""
        if not self.context:
            return
            
        payload = getattr(event_data, "payload", event_data.get("payload", {}) if isinstance(event_data, dict) else {})
        if not payload and hasattr(event_data, "metadata"):
            payload = event_data.metadata
            
        session_id = payload.get("session_id", "default")
        session = self._get_or_create_session(session_id)
        
        status = payload.get("status")
        if status == "SUCCESS" or status == "ExecutionStatus.SUCCESS":
            session.execution_context.last_success = payload
            session.execution_context.completed_workflows.append(payload)
            
            # Construct ConversationArtifact if result contains data
            if "result" in payload:
                from datetime import datetime
                from uuid import uuid4
                
                # Mock affordance extraction based on capability (for demonstration, true logic is generic)
                action = payload.get("action", "unknown")
                affordances = ["Presentation", "Explain"]
                if "search" in action.lower():
                    affordances.extend(["Open Result", "Compare", "Summarize"])
                elif "navigate" in action.lower():
                    affordances.extend(["Navigation", "Traffic", "Routes"])
                    
                artifact = ConversationArtifact(
                    artifact_id=str(uuid4()),
                    artifact_type=f"{action}_result",
                    capability_id=payload.get("capability", "unknown"),
                    timestamp=datetime.now(),
                    summary=f"Result of {action}",
                    structured_result={"data": payload["result"]},
                    referenced_entities=[],
                    supported_followup_actions=affordances,
                    presentation_available=True,
                    expiration_policy="session",
                    confidence=1.0
                )
                session.focus.current_conversation_artifact = artifact
                session.focus.recent_conversation_artifacts.append(artifact)
                session.focus.last_execution = payload
                
        else:
            session.execution_context.last_failure = payload
            session.execution_context.failed_workflows.append(payload)

    def _on_execution_completed(self, event_data: Any):
        """
        Translates canonical ExecutionCompletedEvent into conversational UX.
        (Completes the final mile of the conversation lifecycle)
        """
        if not self.context:
            return
            
        payload = getattr(event_data, "metadata", {})
        status = payload.get("status")
        session_id = "default"
        session = self._get_or_create_session(session_id)
        
        # 1. Update execution context
        if status == "SUCCESS" or status == "LegacyExecutionStatus.SUCCESS":
            session.execution_context.last_success = payload
        else:
            session.execution_context.last_failure = payload

        # 2. Add contextual system prompt describing the outcome
        session.history.append({"role": "system", "content": f"The requested workflow execution completed with status: {status}. Acknowledge this outcome to the user."})
        
        # 3. Generate response using AI Runtime or deterministic fallback
        response_text = ""
        if self.ai_runtime and hasattr(self.ai_runtime, "generate_response"):
            response_text = self.ai_runtime.generate_response(session, intent="StateQueryIntent")
        else:
            if status == "SUCCESS" or status == "LegacyExecutionStatus.SUCCESS":
                response_text = "I've completed that for you."
            elif status == "FAILED" or status == "LegacyExecutionStatus.FAILED":
                response_text = "I couldn't complete that."
            elif status == "PARTIAL_SUCCESS":
                response_text = "I completed some of that, but encountered an issue."
            elif status == "CANCELLED":
                response_text = "I've cancelled that."
            elif status == "TIMED_OUT":
                response_text = "That took too long, so I stopped."
            else:
                response_text = f"The operation finished with status: {status}."
                
        # 4. Add assistant response to history
        session.history.append({"role": "assistant", "content": response_text})
        
        try:
            from desktop.app.memory_contracts import IMemoryService
            memory_service = self.context.registry.resolve(IMemoryService)
            if memory_service and hasattr(memory_service, "append_message_to_history"):
                memory_service.append_message_to_history(session_id, "assistant", response_text)
        except Exception as e:
            logger.warning(f"Failed to append execution outcome to memory: {e}")
            
        # 5. Publish to Presentation Pipeline
        from desktop.models.interaction import ExpressionRequested, ExpressionType
        from desktop.models.presentation import RenderedExpression
        from datetime import datetime
        from uuid import uuid4
        
        correlation_id = getattr(event_data, "correlation_id", str(uuid4()))
        
        if hasattr(self.event_bus, "publish"):
            # Emit abstract cognitive intent for ExpressionRuntime (Rule 180)
            self.event_bus.publish(ExpressionRequested(
                interaction_id=correlation_id,
                correlation_id=correlation_id,
                expression_type=ExpressionType.SPEAK,
                payload={"text": response_text}
            ))
            
            # Emit direct RenderedExpression for fallback routing
            self.event_bus.publish(RenderedExpression(
                timestamp=datetime.now(),
                correlation_id=correlation_id,
                formats={"text": response_text}
            ))
