import os
import sys
import time

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if v3_root not in sys.path:
    sys.path.insert(0, v3_root)

from desktop.character.runtime.runtime.character_runtime import CharacterRuntime
from desktop.character.runtime.scene.character_scene import CharacterScene
from desktop.character.behavior.script.behavior_script import BehaviorScript, ScriptInstruction, LoopCondition

def run_test_tool():
    print("==========================================================")
    print("CHITTI V2 — CHARACTER RUNTIME & SCENE MANAGER ANIMATOR PREVIEW TOOL")
    print("==========================================================\n")
    
    runtime = CharacterRuntime()
    runtime.set_debug_mode(True)
    runtime.start()

    # 1. Behavior & Frame Playback Preview
    behaviors_to_preview = [
        ("CHR_BOOT_001", "Boot"),
        ("CHR_IDLE_001", "Idle"),
        ("CHR_TALK_EXPLAIN_001", "TalkingExplain"),
        ("CHR_GEST_POINT_SCR_001", "PointScreen"),
        ("CHR_SUCC_THUMBSUP_001", "ThumbsUp")
    ]

    for b_id, b_name in behaviors_to_preview:
        print(f"\n---> Previewing Behavior: [{b_id}] {b_name}")
        script = BehaviorScript(
            script_id=f"preview_{b_id.lower()}",
            session_id="preview_session",
            intent_name="PREVIEW",
            instructions=[
                ScriptInstruction(behavior_id=b_id, behavior_name=b_name, loop_condition=LoopCondition("LoopFixedCount", count=2))
            ]
        )
        runtime.execute_script(script)

        for step in range(14):
            frame_path = runtime.tick(dt=0.071)
            frame_str = os.path.basename(frame_path) if frame_path else "None"
            print(f"     Frame {step+1:02d}/14 -> Played: {frame_str}")
            time.sleep(0.01)

    # 2. Scene Manager & Recovery Simulation
    print("\n---> Simulating Scene Manager Transitions & Scene Recovery...")
    sm = runtime.scene_manager
    sm.transition_to_scene(CharacterScene.WORKING)
    print(f"     Active Scene: {sm.current_scene.value}")
    
    # Interrupt WORKING scene with high-priority REMINDER scene
    sm.transition_to_scene(CharacterScene.REMINDER)
    print(f"     Interrupted! Active Scene: {sm.current_scene.value} | Stack: {[s.value for s in sm.metrics.scene_stack]}")
    
    # Complete REMINDER scene and restore WORKING scene
    sm.complete_current_scene()
    print(f"     Completed! Restored Scene: {sm.current_scene.value} | Stack: {[s.value for s in sm.metrics.scene_stack]}")

    runtime.stop()
    print("\n==========================================================")
    print("ANIMATOR & SCENE PREVIEW COMPLETE")
    print("==========================================================")

if __name__ == "__main__":
    run_test_tool()
