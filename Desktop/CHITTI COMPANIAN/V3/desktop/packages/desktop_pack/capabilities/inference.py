from typing import Any, Dict
from datetime import datetime
from uuid import uuid4
from desktop.packages.sdk.pack_metadata import CapabilityMetadata
from desktop.models.presentation import RenderedExpression

class ChatResponseCapability:
    def __init__(self, ai_runtime, event_bus):
        self.metadata = CapabilityMetadata(category="Inference", supports_undo=False)
        self.ai_runtime = ai_runtime
        self.event_bus = event_bus

    def execute(self, context: 'CapabilityContext') -> 'ExecutionResult':
        text = context.payload.get("text", "")
        if context.logger:
            context.logger.info(f"[ChatResponseCapability] Processing LLM response for: {text}")
        
        if not hasattr(self.ai_runtime, "_history"):
            self.ai_runtime._history = []
            
        self.ai_runtime._history.append({"role": "user", "content": text})
        
        system_prompt = {"role": "system", "content": "You are CHITTI, a helpful desktop AI companion. Provide brief, friendly answers."}
        messages = [system_prompt] + self.ai_runtime._history[-10:]
        
        try:
            raw_response = self.ai_runtime.generate(messages, tools_enabled=False)
            response_text = raw_response.get("text", "I'm sorry, I couldn't generate a response.")
        except Exception as e:
            response_text = f"LLM Error: {str(e)}"
        
        self.ai_runtime._history.append({"role": "assistant", "content": response_text})
        
        if self.event_bus:
            self.event_bus.publish(RenderedExpression(
                timestamp=datetime.now(),
                correlation_id=str(uuid4()),
                formats={"text": response_text}
            ))
            
        from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
        return ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            outputs={"response": response_text}
        )
