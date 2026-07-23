import uuid
from typing import Any
from desktop.orchestrator.response_composer import ResponseComposer

class SessionState:
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"
    INTERRUPTED = "INTERRUPTED"

class InteractionSession:
    def __init__(self, cognitive_pipeline, input_adapter, response_composer: ResponseComposer):
        self.interaction_id = "ix_" + str(uuid.uuid4())
        self.pipeline_correlation_id = None
        self.conversation_id = "conv_" + str(uuid.uuid4())
        self.state = SessionState.IDLE
        self.cognitive_pipeline = cognitive_pipeline
        self.input_adapter = input_adapter
        self.response_composer = response_composer

    def ingest_input(self, raw_input: Any):
        self.state = SessionState.LISTENING
        experience = self.input_adapter.translate(raw_input)
        
        self.pipeline_correlation_id = getattr(experience, "experience_id", "ctx_" + str(uuid.uuid4()))
        self.state = SessionState.PROCESSING
        
        try:
            execution_result = self.cognitive_pipeline.process(experience)
            
            if self.state == SessionState.INTERRUPTED:
                return
                
            self.state = SessionState.SPEAKING
            self.response_composer.compose(execution_result)
        except Exception as e:
            print(f"[SESSION_ERROR] Pipeline exception: {e}")
        finally:
            if self.state != SessionState.INTERRUPTED:
                self.state = SessionState.IDLE

    def interrupt(self):
        self.state = SessionState.INTERRUPTED
        self.response_composer.interrupt()
