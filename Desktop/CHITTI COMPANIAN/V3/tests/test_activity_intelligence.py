from datetime import datetime, timedelta
import uuid
from desktop.models.observation import Observation
from desktop.platform.activity.engine import ActivityIntelligenceEngine

def create_obs(otype: str, payload: dict, time_offset_sec: int = 0) -> Observation:
    return Observation(
        observation_id=str(uuid.uuid4()),
        correlation_id=str(uuid.uuid4()),
        session_id="test_session",
        observation_type=otype,
        timestamp=datetime.now() + timedelta(seconds=time_offset_sec),
        source="TestSource",
        payload=payload
    )

def run_tests():
    print("--- Running Sprint 20 Activity Intelligence Regression Suite ---")
    engine = ActivityIntelligenceEngine()
    
    # 1. Coding Session & Session Start
    obs_ide = create_obs("window_state", {"title": "app.py - Visual Studio Code"}, 0)
    engine.process_observation(obs_ide)
    assert engine.active_session is not None, "Failed to start session"
    assert engine.active_session.activity_type == "Coding Activity", "Failed to classify Coding Session"
    print("[PASS] Session start & Coding Session classification.")
    
    # 2. Session Update & File Modification
    obs_file = create_obs("filesystem_state", {"filepath": "app.py"}, 5)
    engine.process_observation(obs_file)
    assert len(engine.active_session.related_observations) == 2, "Failed to update session with related observations"
    assert engine.active_session.last_update == obs_file.timestamp, "Failed to update last_update timestamp"
    print("[PASS] Session update & File modification correlation.")
    
    # 3. Multi-window coding session (Same activity type, different window)
    obs_ide2 = create_obs("window_state", {"title": "utils.py - Visual Studio Code"}, 10)
    engine.process_observation(obs_ide2)
    assert engine.active_session.activity_type == "Coding Activity", "Failed multi-window coding session"
    print("[PASS] Multi-window coding session.")
    
    # 4. Context Switch & Session Closure (Writing Session)
    obs_docs = create_obs("window_state", {"title": "Project Spec - Google Docs"}, 20)
    engine.process_observation(obs_docs)
    assert len(engine.emitted_events) == 1, "Failed to emit event upon context switch"
    coding_event = engine.emitted_events[0]
    assert coding_event.activity_type == "Coding Activity", "Closed event type mismatch"
    assert coding_event.duration == 10.0, "Duration calculation failed" # 10 - 0 = 10
    
    assert engine.active_session.activity_type == "Writing Activity", "Failed to start new context (Writing Session)"
    print("[PASS] Context switch & Session closure & Writing Session classification.")
    
    # 5. Consecutive Sessions (Web Research + Clipboard)
    obs_browser = create_obs("window_state", {"title": "Python Docs - Chrome"}, 30)
    engine.process_observation(obs_browser)
    obs_clip = create_obs("clipboard_state", {"type": "text"}, 35)
    engine.process_observation(obs_clip)
    
    assert len(engine.emitted_events) == 2, "Failed to emit consecutive session event"
    assert engine.active_session.activity_type == "Web Research", "Failed Web Research / Clipboard classification"
    print("[PASS] Consecutive sessions, Web Research, and Clipboard-assisted activity.")
    
    # 6. Build Session
    obs_build = create_obs("process_state", {"name": "python.exe"}, 40)
    engine.process_observation(obs_build)
    
    assert engine.active_session.activity_type == "Build Activity", "Failed Build Session classification"
    print("[PASS] Build Session classification.")
    
    # Flush final session
    engine._close_active_session(obs_build.timestamp + timedelta(seconds=10))
    assert len(engine.emitted_events) == 4, "Final flush failed"
    
    print("\n✓ Session start")
    print("✓ Session update")
    print("✓ Session closure")
    print("✓ Context switch")
    print("✓ Consecutive sessions")
    print("✓ Multi-window coding session")
    print("✓ Coding Session")
    print("✓ Writing Session")
    print("✓ Web Research Session")
    print("✓ Build Session")
    print("✓ Clipboard-assisted activity")
    print("✓ File modification correlation")
    print("\nAll Activity Intelligence regression scenarios passed successfully!")

if __name__ == "__main__":
    run_tests()
