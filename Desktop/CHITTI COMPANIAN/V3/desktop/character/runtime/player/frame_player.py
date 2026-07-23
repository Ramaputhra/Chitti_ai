import logging
from typing import Optional, List
from desktop.character.runtime.player.animation_clock import AnimationClock
from desktop.character.runtime.assets.asset_loader import LoadedBehaviorClip

logger = logging.getLogger(__name__)

class FramePlayer:
    """
    S36B: 2D PNG Frame Player managing frame index playback, 14 FPS timing, pause, resume, seek, restart, loop, and stop.
    """
    def __init__(self, fps: float = 14.0):
        self.clock = AnimationClock(target_fps=fps)
        self.current_clip: Optional[LoadedBehaviorClip] = None
        self.current_frame_index = 0
        self.is_playing = False
        self.is_paused = False
        self._accumulator = 0.0

    def load_clip(self, clip: LoadedBehaviorClip):
        self.current_clip = clip
        fps_override = clip.metadata.get("fps", 14)
        self.clock.set_fps(fps_override)
        self.current_frame_index = 0
        self._accumulator = 0.0

    def play(self):
        if self.current_clip and self.current_clip.frame_paths:
            self.is_playing = True
            self.is_paused = False
            self.clock.reset()

    def pause(self):
        self.is_paused = True
        self.clock.paused = True

    def resume(self):
        self.is_paused = False
        self.clock.paused = False

    def stop(self):
        self.is_playing = False
        self.is_paused = False
        self.current_frame_index = 0

    def seek(self, frame_index: int):
        if self.current_clip and self.current_clip.frame_paths:
            self.current_frame_index = max(0, min(frame_index, len(self.current_clip.frame_paths) - 1))

    def update(self, dt: float) -> Optional[str]:
        if not self.is_playing or self.is_paused or not self.current_clip or not self.current_clip.frame_paths:
            return self.get_current_frame_path()

        self._accumulator += dt
        frame_dur = self.clock.frame_duration

        while self._accumulator >= frame_dur:
            self._accumulator -= frame_dur
            self.current_frame_index += 1

            if self.current_frame_index >= len(self.current_clip.frame_paths):
                loop = self.current_clip.metadata.get("loop", False)
                if loop:
                    self.current_frame_index = 0
                else:
                    self.current_frame_index = len(self.current_clip.frame_paths) - 1
                    self.is_playing = False
                    break

        return self.get_current_frame_path()

    def get_current_frame_path(self) -> Optional[str]:
        if self.current_clip and self.current_clip.frame_paths:
            idx = min(self.current_frame_index, len(self.current_clip.frame_paths) - 1)
            return self.current_clip.frame_paths[idx]
        return None
