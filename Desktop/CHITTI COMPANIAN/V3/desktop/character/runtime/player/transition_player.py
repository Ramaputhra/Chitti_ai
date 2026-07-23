import logging
from typing import Optional
from desktop.character.runtime.player.clip_player import ClipPlayer

logger = logging.getLogger(__name__)

class TransitionPlayer:
    """
    S36B: Transition Player layer blending smooth transition clips between behavior states.
    """
    def __init__(self, clip_player: ClipPlayer):
        self.clip_player = clip_player
        self.in_transition = False

    def play_transition(self, transition_behavior_id: str) -> bool:
        logger.info(f"[TransitionPlayer] Blending transition '{transition_behavior_id}'")
        self.in_transition = True
        ok = self.clip_player.play_clip(transition_behavior_id)
        return ok

    def update(self, dt: float) -> Optional[str]:
        frame_path = self.clip_player.update(dt)
        if not self.clip_player.frame_player.is_playing:
            self.in_transition = False
        return frame_path
