import logging
import time
from typing import Dict, Any

from desktop.models.presentation_models import PresentationProfile, SpeechPersona, PresenceState
from desktop.models.execution_models import ExecutionContext, ExecutionStatus, VerificationCompletedEvent
from desktop.platform.core.response_builder import ResponseBuilder
from desktop.platform.core.persona_engine import PersonaEngine
from desktop.platform.core.presence_runtime import PresenceRuntime
from desktop.platform.core.presentation_runtime import PresentationRuntime
from desktop.platform.components.adapters.expression_adapter import ExpressionAdapter

class MockEventBus:
    def __init__(self):
        self.published_events = []
    def publish(self, event_type: str, source: str, payload: Dict[str, Any] = None) -> None:
        self.published_events.append((event_type, payload))

def run_presentation_tests():
    logging.basicConfig(level=logging.INFO)
    print("\n--- Running Phase 5.5 Presentation Engine Tests ---")
    
    bus = MockEventBus()
    
    # Setup Phase 5.5
    profile = PresentationProfile(
        speech_persona=SpeechPersona(formal=0.5, friendly=0.3, humour=0.2), # Within limits
        sound_effects=True
    )
    
    response_builder = ResponseBuilder(bus)
    persona_engine = PersonaEngine(profile)
    presence_runtime = PresenceRuntime(bus)
    expression_adapter = ExpressionAdapter()
    
    presentation = PresentationRuntime(
        event_bus=bus,
        response_builder=response_builder,
        persona_engine=persona_engine,
        presence_runtime=presence_runtime,
        expression_adapter=expression_adapter
    )
    
    def get_types():
        return [e[0] for e in bus.published_events]

    # --- Test 1: Formal Success (Open Downloads) ---
    print("\n[TEST 1: Verification Completed -> Persona -> Expression -> Follow Up]")
    context = ExecutionContext(workflow_id="wf-test", step_id="s1", capability_id="sys.folder.open", parameters={"folder_path": "downloads"})
    
    # Mocking that verification finished successfully
    ver_event = VerificationCompletedEvent(context=context, status=ExecutionStatus.SUCCESS, confidence=1.0)
    
    presentation.handle_verification_completed({"event": ver_event})
    
    types = get_types()
    assert "RESPONSE_CREATED" in types
    print("✅ RESPONSE_CREATED (Builder converted verified fact)")
    assert "PRESENTATION_STARTED" in types
    print("✅ PRESENTATION_STARTED (Persona engine computed sliders)")
    assert "FOLLOW_UP_WINDOW_OPENED" in types
    print("✅ FOLLOW_UP_WINDOW_OPENED (Presence Engine shift)")
    assert "PRESENCE_STATE_CHANGED" in types
    print("✅ PRESENCE_STATE_CHANGED (IDLE -> FOLLOW_UP_WINDOW)")
    assert "PRESENTATION_COMPLETED" in types
    print("✅ PRESENTATION_COMPLETED (End of Experience 001 Loop)")
    
if __name__ == "__main__":
    run_presentation_tests()
