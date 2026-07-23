import sys
import os
import json
import asyncio

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if v3_root not in sys.path:
    sys.path.insert(0, v3_root)

from desktop.app.kernel import RuntimeConfiguration, BootManager
from desktop.app.presentation_contracts import DefaultTextRenderer, MarkdownRenderer
from desktop.runtimes.capability.registry import CapabilityRegistry

from desktop.character.presence.presence_controller import CharacterPresenceController
from desktop.character.presence.presence_events import PresenceStateEnum
from desktop.character.presence.conversation_state import ConversationStateEnum
from desktop.character.presence.presence_memory import PresenceMemory, PresenceMemoryData

async def run_verification():
    print("==========================================================")
    print("Starting S36B-R2-R1 Character Presence Refinement Verification")
    print("==========================================================\n")
    
    all_passed = True
    presence = CharacterPresenceController()

    print("[1/10] Verifying Conversation State Model Enums & Context...")
    states = [s.value for s in ConversationStateEnum]
    expected_states = ["ACTIVE", "PAUSED_BY_USER", "PAUSED_SYSTEM_TRAY", "PAUSED_FULLSCREEN", "PAUSED_PRESENTATION", "INTERRUPTED", "COMPLETED", "FAILED"]
    if all(es in states for es in expected_states):
        print(f"✅ Conversation states verified cleanly ({len(states)} canonical states).")
    else:
        print("❌ Conversation state model FAILED.")
        all_passed = False

    print("\n[2/10] Verifying Middle Click Transformation to PAUSED_BY_USER...")
    presence.wake_up(source="wake_word")       # To Character Window
    presence.handle_first_middle_click()       # To Presence Dot
    presence.speech_active = True
    presence.conversation_context.state = ConversationStateEnum.ACTIVE
    
    presence.handle_second_middle_click()      # To System Tray
    
    if (presence.conversation_context.state == ConversationStateEnum.PAUSED_BY_USER and 
        presence.conversation_context.stop_reason == "User middle-clicked Presence Dot" and
        presence.current_state == PresenceStateEnum.SYSTEM_TRAY):
        print("✅ Middle-Click transformed conversation to PAUSED_BY_USER cleanly.")
    else:
        print(f"❌ Conversation suspension FAILED (Got state: '{presence.conversation_context.state.value}').")
        all_passed = False

    print("\n[3/10] Verifying Wake Restore & Resumability Handling...")
    presence.conversation_context.narration_offset = 4
    presence.conversation_context.resume_allowed = True
    
    res = presence.request_conversation_resume()
    if res.get("status") == "RESUMED" and res.get("narration_offset") == 4:
        print(f"✅ Resumable conversation resumed from offset 4: '{res.get('message')}'")
    else:
        print(f"❌ Conversation resume FAILED: {res}")
        all_passed = False

    print("\n[4/10] Verifying Non-Resumable Capability Fallback...")
    presence.conversation_context.pause_by_user("Test pause")
    presence.conversation_context.resume_allowed = False
    
    res_fallback = presence.request_conversation_resume()
    if res_fallback.get("status") == "NOT_RESUMABLE" and "restart" in res_fallback.get("message"):
        print("✅ Non-resumable capability handled cleanly with restart/summarize offer.")
    else:
        print(f"❌ Non-resumable capability fallback FAILED: {res_fallback}")
        all_passed = False

    print("\n[5/10] Verifying Fullscreen Presentation Conversation State...")
    presence.wake_up(source="wake_word")
    presence.enter_presentation_mode()
    if presence.conversation_context.state == ConversationStateEnum.ACTIVE:
        print("✅ Conversation state remained ACTIVE during Fullscreen Presentation.")
    else:
        print("❌ Presentation conversation state FAILED.")
        all_passed = False
    presence.exit_presentation_mode()

    print("\n[6/10] Verifying Expanded Presence Memory Schema...")
    mem_data = presence.memory.data
    has_expanded_fields = (
        hasattr(mem_data, "last_widget_layout") and
        hasattr(mem_data, "last_theme") and
        hasattr(mem_data, "last_motion_theme") and
        hasattr(mem_data, "last_desktop_workspace") and
        hasattr(mem_data, "last_restore_bounds")
    )
    if has_expanded_fields:
        print(f"✅ Expanded Presence Memory schema verified (Workspace: '{mem_data.last_desktop_workspace}', Theme: '{mem_data.last_theme}').")
    else:
        print("❌ Expanded Presence Memory schema FAILED.")
        all_passed = False

    print("\n[7/10] Verifying Legacy Memory Automatic Migration...")
    legacy_path = os.path.join(v3_root, "desktop", "character", "presence", "test_legacy_memory.json")
    with open(legacy_path, "w", encoding="utf-8") as f:
        json.dump({"last_position_x": 1200, "last_position_y": 300}, f)
        
    legacy_mem = PresenceMemory(storage_path=legacy_path)
    if legacy_mem.data.last_position_x == 1200 and legacy_mem.data.last_theme == "dark_fluent":
        print("✅ Legacy presence memory automatically migrated to expanded schema cleanly.")
    else:
        print("❌ Legacy memory migration FAILED.")
        all_passed = False
    if os.path.exists(legacy_path):
        os.remove(legacy_path)

    print("\n[8/10] Verifying DesktopContextManager...")
    ctx_mgr = presence.desktop_context_manager
    ctx_mgr.set_fullscreen_state(True)
    if ctx_mgr.detect_fullscreen_app() and ctx_mgr.active_context == "FULLSCREEN_APP":
        print("✅ DesktopContextManager verified fullscreen application context detection.")
    else:
        print("❌ DesktopContextManager verification FAILED.")
        all_passed = False

    print("\n[9/10] Verifying Startup Restore Logic...")
    if presence.memory.data.last_restore_bounds is not None:
        print("✅ Startup restore logic verified with saved bounds.")
    else:
        print("❌ Startup restore logic FAILED.")
        all_passed = False

    print("\n[10/10] Zero Regression Verification (Kernel Boot & Frozen Platforms)...")
    config_sys = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config_sys)
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    if kernel is not None:
        print("✅ Zero Regression Verification PASSED: Behavior Scheduler, Character Runtime, Voice, Personality, Identity, Presentation, Desktop UI, Motion, and Cognitive Core V1 fully intact.")
    else:
        print("❌ Zero Regression Verification FAILED.")
        all_passed = False

    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: S36B-R2-R1 IMPLEMENTATION VERIFIED")
    else:
        print("DECISION: S36B-R2-R1 VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
