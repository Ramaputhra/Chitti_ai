import logging
from typing import Dict, Any

class MockEventBus:
    def __init__(self):
        self.subscribers = {}
        self.published_events = []

    def subscribe(self, event_type: str, callback: Any) -> None:
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type: str, source: str, payload: Dict[str, Any] = None) -> None:
        self.published_events.append((event_type, payload))
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(payload) # SemanticRuntime expects raw payload dict here

from desktop.platform.ai.semantic_runtime import SemanticRuntime
from desktop.models.semantic_models import IntentType, AmbiguityReason

def run_semantic_test():
    logging.basicConfig(level=logging.INFO)
    print("\n--- Running Semantic Runtime Tests ---")
    
    bus = MockEventBus()
    runtime = SemanticRuntime(bus)
    
    def get_last_event():
        return bus.published_events[-1]
        
    # --- 1. Golden Path ---
    print("\n[TEST 1: Golden Path]")
    bus.publish("USER_TRANSCRIPT_GENERATED", "Whisper", {"payload": {"text": "Open Downloads", "language": "en"}})
    event_type, payload = get_last_event()
    assert event_type == "INTENT_GENERATED"
    intent = payload["event"].desktop_intent
    assert intent.action == IntentType.OPEN
    assert intent.target == "Downloads"
    print("✅ Success: Golden Path")

    # --- 2. Synonym Test ---
    print("\n[TEST 2: Synonym Test]")
    bus.publish("USER_TRANSCRIPT_GENERATED", "Whisper", {"payload": {"text": "Show Downloads", "language": "en"}})
    event_type, payload = get_last_event()
    assert event_type == "INTENT_GENERATED"
    intent = payload["event"].desktop_intent
    assert intent.action == IntentType.OPEN
    assert intent.target == "Downloads"
    print("✅ Success: Synonym 'Show' normalized to OPEN")

    # --- 3. Ambiguity Test ---
    print("\n[TEST 3: Ambiguity Test]")
    bus.publish("USER_TRANSCRIPT_GENERATED", "Whisper", {"payload": {"text": "Open it", "language": "en"}})
    event_type, payload = get_last_event()
    assert event_type == "INTENT_AMBIGUOUS"
    assert payload["event"].reason == AmbiguityReason.UNKNOWN_TARGET
    print("✅ Success: Pronoun 'it' flagged as UNKNOWN_TARGET")

    # --- 4. Multilingual Test ---
    print("\n[TEST 4: Multilingual Test]")
    bus.publish("USER_TRANSCRIPT_GENERATED", "Whisper", {"payload": {"text": "Downloads తెరువు", "language": "te"}})
    event_type, payload = get_last_event()
    assert event_type == "INTENT_GENERATED"
    intent = payload["event"].desktop_intent
    assert intent.action == IntentType.OPEN
    assert intent.target == "Downloads"
    print("✅ Success: Telugu normalized to generic OPEN intent")

    # --- 5. Unknown Command Test ---
    print("\n[TEST 5: Unknown Command]")
    bus.publish("USER_TRANSCRIPT_GENERATED", "Whisper", {"payload": {"text": "Fly to the moon", "language": "en"}})
    event_type, payload = get_last_event()
    assert event_type == "INTENT_AMBIGUOUS"
    assert payload["event"].reason == AmbiguityReason.UNKNOWN_ACTION
    print("✅ Success: Unrecognized action caught")

    # --- 6. Missing Parameter Test ---
    print("\n[TEST 6: Missing Parameter]")
    bus.publish("USER_TRANSCRIPT_GENERATED", "Whisper", {"payload": {"text": "Move report", "language": "en"}})
    event_type, payload = get_last_event()
    assert event_type == "INTENT_AMBIGUOUS"
    assert payload["event"].reason == AmbiguityReason.MISSING_PARAMETER
    print("✅ Success: MOVE command blocked without destination parameter")

if __name__ == "__main__":
    run_semantic_test()
