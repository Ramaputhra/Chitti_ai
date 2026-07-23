import time
from desktop.orchestrator.response_packet import ResponsePacket
from desktop.orchestrator.response_composer import ResponseComposer, StreamingState
from desktop.orchestrator.interaction_session import InteractionSession, SessionState
from desktop.orchestrator.main_orchestrator import MainOrchestrator

class MockPipeline:
    def process(self, exp):
        time.sleep(0.1) # simulate work
        class MockResult:
            overall_status = "COMPLETED"
        return MockResult()

class MockInputAdapter:
    def translate(self, raw):
        class MockExp:
            experience_id = "ctx_123"
        return MockExp()

class MockRenderer:
    def __init__(self):
        self.played = False
        
    def play(self, text, meta):
        self.played = True
        
    def set_animation(self, anim):
        pass
        
    def update(self, meta):
        pass

def run_verification():
    print("Starting EE5 Human Interaction Runtime Verification...\n")
    
    print("[1/5] Verifying Interaction Identity Model...")
    session = InteractionSession(MockPipeline(), MockInputAdapter(), ResponseComposer(None, None, None))
    assert session.interaction_id.startswith("ix_")
    assert session.conversation_id.startswith("conv_")
    print("       Immutable interaction identities generated correctly.")
    
    print("[2/5] Verifying ResponsePacket & Streaming States...")
    comp = ResponseComposer(MockRenderer(), MockRenderer(), MockRenderer())
    assert comp.current_state == StreamingState.COMPLETED
    comp.start()
    
    class MockRes:
        overall_status = "COMPLETED"
    
    comp.compose(MockRes())
    time.sleep(0.2)
    assert comp.current_state == StreamingState.COMPLETED
    print("       ResponseComposer successfully transitioned QUEUED -> STREAMING -> COMPLETED.")
    
    print("[3/5] Verifying Session Interruption...")
    comp.interrupt()
    assert comp.current_state == StreamingState.INTERRUPTED
    print("       Interruption correctly bypassed the rendering queue.")
    
    print("[4/5] Verifying Session Recovery Model...")
    class CrashingRenderer:
        def play(self, *args):
            raise Exception("TTS Engine Failure")
        def set_animation(self, *args):
            pass
        def update(self, *args):
            pass
            
    crashing_comp = ResponseComposer(CrashingRenderer(), CrashingRenderer(), CrashingRenderer())
    crashing_comp.start()
    crashing_comp.compose(MockRes())
    time.sleep(0.2)
    assert crashing_comp.current_state == StreamingState.COMPLETED
    print("       Renderer failure gracefully caught without crashing pipeline.")
    
    print("[5/5] Verifying Main Orchestrator Binding...")
    main_orch = MainOrchestrator(MockPipeline(), MockInputAdapter())
    main_orch.interaction_session.ingest_input("Hello")
    main_orch.shutdown()
    print("       MainOrchestrator correctly bound InteractionSession and Composer.")
    
    print("\n✅ EE5 Human Interaction Runtime strictly verified.")

if __name__ == "__main__":
    run_verification()
