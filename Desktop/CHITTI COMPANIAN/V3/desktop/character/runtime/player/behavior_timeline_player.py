import logging
from typing import Optional
from desktop.character.behavior.timeline.behavior_timeline import BehaviorTimeline
from desktop.character.runtime.player.clip_player import ClipPlayer
from desktop.character.runtime.player.transition_player import TransitionPlayer

logger = logging.getLogger(__name__)

class BehaviorTimelinePlayer:
    """
    S36B: Behavior Timeline Player playing timestamped BehaviorTimeline objects.
    """
    def __init__(self, clip_player: ClipPlayer):
        self.clip_player = clip_player
        self.transition_player = TransitionPlayer(clip_player)
        self.current_timeline: Optional[BehaviorTimeline] = None
        self.current_event_idx = 0
        self.elapsed_time = 0.0
        self.is_playing = False

    def play_timeline(self, timeline: BehaviorTimeline):
        self.current_timeline = timeline
        self.current_event_idx = 0
        self.elapsed_time = 0.0
        self.is_playing = True
        logger.info(f"[BehaviorTimelinePlayer] Playing timeline '{timeline.timeline_id}' ({len(timeline.events)} events)")
        if timeline.events:
            first_evt = timeline.events[0]
            self.clip_player.play_clip(first_evt.behavior_id)

    def update(self, dt: float) -> Optional[str]:
        if not self.is_playing or not self.current_timeline or not self.current_timeline.events:
            return None

        self.elapsed_time += dt
        evt = self.current_timeline.events[self.current_event_idx]

        if self.elapsed_time >= (evt.start_time + evt.duration):
            self.current_event_idx += 1
            if self.current_event_idx >= len(self.current_timeline.events):
                self.is_playing = False
                logger.info(f"[BehaviorTimelinePlayer] Timeline '{self.current_timeline.timeline_id}' completed.")
                return None
            
            next_evt = self.current_timeline.events[self.current_event_idx]
            self.clip_player.play_clip(next_evt.behavior_id)

        return self.clip_player.update(dt)
