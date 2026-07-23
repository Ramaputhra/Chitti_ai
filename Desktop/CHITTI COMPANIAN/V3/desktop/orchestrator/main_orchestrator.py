from desktop.orchestrator.interaction_session import InteractionSession
from desktop.orchestrator.response_composer import ResponseComposer

class MainOrchestrator:
    def __init__(self, cognitive_pipeline, input_adapter, tts_renderer=None, ui_renderer=None, character_renderer=None):
        self.cognitive_pipeline = cognitive_pipeline
        self.input_adapter = input_adapter
        self.response_composer = ResponseComposer(tts_renderer, ui_renderer, character_renderer)
        self.response_composer.start()
        
        self.interaction_session = InteractionSession(
            self.cognitive_pipeline, 
            self.input_adapter, 
            self.response_composer
        )

    def shutdown(self):
        self.response_composer.stop()
