import time
from typing import Optional, List
from desktop.character.behavior.script.behavior_script import BehaviorScript
from desktop.character.behavior.timeline.behavior_timeline import BehaviorTimeline
from desktop.character.behavior.timeline.timeline_event import TimelineEvent
from desktop.character.behavior.speech.speech_context import SpeechContext
from desktop.character.behavior.scheduler.behavior_transition_manager import BehaviorTransitionManager

class BehaviorTimelineCompiler:
    """
    S34B-R1: Converts declarative BehaviorScript into a concrete, timestamped BehaviorTimeline.
    Only Character Runtime consumes BehaviorTimeline.
    """
    def __init__(self):
        self.transition_mgr = BehaviorTransitionManager()

    def compile(
        self,
        script: BehaviorScript,
        speech_context: Optional[SpeechContext] = None
    ) -> BehaviorTimeline:
        timeline = BehaviorTimeline(
            timeline_id=f"compiled_{script.script_id}",
            session_id=script.session_id,
            created_at=time.time()
        )

        speech_duration = speech_context.timeline.total_duration if (speech_context and speech_context.timeline) else 2.0
        curr_t = 0.0

        for inst in script.instructions:
            # Resolve duration and loop count based on loop_condition
            dur = 1.0
            loop_count = 1

            if inst.loop_condition:
                c_type = inst.loop_condition.condition_type
                if c_type == "LoopUntilSpeechEnds":
                    dur = speech_duration
                    loop_count = int(speech_duration / 1.2) + 1
                elif c_type == "LoopUntilExecutionCompletes":
                    dur = 3.0
                    loop_count = 3
                elif c_type == "LoopForever":
                    dur = 10.0
                    loop_count = 0
                elif c_type == "LoopFixedCount":
                    loop_count = inst.loop_condition.count
                    dur = max(0.5, loop_count * 0.8)

            # Insert transition if needed
            if timeline.events:
                last_evt = timeline.events[-1]
                trans = self.transition_mgr.get_transition(
                    last_evt.behavior_name,
                    inst.behavior_name,
                    start_time=curr_t
                )
                if trans:
                    timeline.add_event(trans)
                    curr_t += trans.duration

            evt = TimelineEvent(
                behavior_id=inst.behavior_id,
                behavior_name=inst.behavior_name,
                start_time=curr_t,
                duration=dur,
                loop_count=loop_count,
                priority=inst.priority,
                interruptible=inst.interruptible
            )
            timeline.add_event(evt)
            curr_t += dur

        return timeline
