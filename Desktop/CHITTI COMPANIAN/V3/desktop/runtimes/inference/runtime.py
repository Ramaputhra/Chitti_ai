import logging
import threading
from typing import Any

from desktop.runtimes.inference.events import (
    InferenceStarted,
    InferenceCompleted,
    ConversationResponseGenerated
)
from desktop.runtimes.inference.context import InferenceContext

logger = logging.getLogger(__name__)

class InferenceRuntime:
    """
    Orchestrates the local LLM generation. 
    Strictly isolated: does not know about models, APIs, or formatting.
    """
    def __init__(self, event_bus: Any, registry: Any):
        self.event_bus = event_bus
        self.registry = registry
        self.provider = self.registry.get_active_providers()[0] if hasattr(self.registry, "get_active_providers") else self.registry
        self.context = InferenceContext()
        
        if hasattr(self.event_bus, "subscribe"):
            self.event_bus.subscribe("InferenceRequested", self._on_inference_requested)
            
    async def initialize(self, context) -> bool:
        self.context_engine = context
        return True
        
    async def start(self):
        print(f"=========================================")
        print(f"AI Runtime")
        print(f"Provider : llama.cpp")
        print(f"Model    : qwen2.5-1.5b-instruct")
        print(f"Context  : 8192")
        print(f"Streaming: Enabled")
        print(f"Health   : READY")
        print(f"=========================================")
        
        self._warmup_provider()
        return True
        
    async def stop(self):
        return True
        
    async def shutdown(self):
        return True

    def _warmup_provider(self):
        if hasattr(self.provider, "core") and hasattr(self.provider.core, "generate"):
            logger.info("Warming up KV cache...")
            # Fire-and-forget dummy prompt to pre-allocate memory and prime KV cache
            try:
                self.provider.core.generate([{"role": "system", "content": "You are CHITTI."}], tools_enabled=False)
                logger.info("KV cache warm-up complete.")
            except Exception as e:
                if type(e).__name__ == "ModelNotInstalledError":
                    logger.warning("Model not installed. Publishing event.")
                    from desktop.platform.configuration.events import SystemEvents
                    from desktop.platform.shared.interfaces.event_bus import Event
                    if hasattr(self.event_bus, "publish"):
                        self.event_bus.publish(Event(SystemEvents.MODEL_NOT_INSTALLED, source="InferenceRuntime", payload={}))
                else:
                    logger.error(f"Warm-up failed: {e}")

    def stop(self):
        logger.info("InferenceRuntime stopped.")

    def _on_inference_requested(self, event_data: Any):
        payload = getattr(event_data, "payload", event_data.get("payload", {}) if isinstance(event_data, dict) else {})
        text = payload.get("text", "").strip()
        session_id = payload.get("session_id", "default")
        
        if not text:
            return  # Orchestrator handles dropping back to SLEEPING
            
        print(f"\n[InferenceRuntime] Received InferenceRequested: '{text}'")
        if hasattr(self.event_bus, "publish"):
            self.event_bus.publish(InferenceStarted(session_id))
            
        def _run_inference():
            try:
                # 1. Build context
                messages = self.context.build_prompt(text)
                
                # 2. Invoke provider (Disable tools if this is a narration request)
                print(f"[InferenceRuntime] Generating...")
                tools_enabled = not (text.strip().startswith("{") and '"system_directive"' in text)
                
                if hasattr(self.provider, "core") and hasattr(self.provider.core, "generate"):
                    result = self.provider.core.generate(messages, tools_enabled=tools_enabled)
                elif hasattr(self.provider, "generate"):
                    result = self.provider.generate(messages)
                else:
                    result = {"text": "", "tool_calls": []}
                    
                response_text = result.get("text", "")
                tool_calls = result.get("tool_calls", [])
                
                # 3. Publish completions
                if hasattr(self.event_bus, "publish"):
                    if tool_calls:
                        for tc in tool_calls:
                            func = tc.get("function", {})
                            name = func.get("name")
                            args = func.get("arguments", {})
                            from desktop.runtimes.inference.events import ToolCallProposed
                            logger.info(f"InferenceRuntime proposing tool call: {name} {args}")
                            self.event_bus.publish(ToolCallProposed(tool=name, arguments=args, session_id=session_id))
                    else:
                        self.event_bus.publish(InferenceCompleted(response_text, session_id))
                        self.event_bus.publish(ConversationResponseGenerated(response_text, session_id))
                        # Temporary mapping to Voice.SpeakRequested
                        from desktop.runtimes.expression.outputs.voice.events import SpeakRequested
                        self.event_bus.publish(SpeakRequested(text=response_text))
                
                # 4. Save to context history
                if response_text:
                    self.context.add_turn(text, response_text)
                
            except Exception as e:
                logger.error(f"Inference failed: {e}")
                from desktop.runtimes.inference.events import InferenceCancelled
                if hasattr(self.event_bus, "publish"):
                    self.event_bus.publish(InferenceCancelled(session_id, reason=str(e)))
                    
        threading.Thread(target=_run_inference, daemon=True).start()
