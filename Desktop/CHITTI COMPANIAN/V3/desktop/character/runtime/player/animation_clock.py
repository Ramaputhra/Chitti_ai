import time

class AnimationClock:
    """
    S36B: High-precision Animation Clock providing delta time, frame timing, total playback time, and synchronization.
    """
    def __init__(self, target_fps: float = 14.0):
        self.target_fps = target_fps
        self.frame_duration = 1.0 / target_fps
        self._last_tick = time.time()
        self.total_playback_time = 0.0
        self.paused = False

    def tick(self) -> float:
        now = time.time()
        dt = now - self._last_tick
        self._last_tick = now
        if not self.paused:
            self.total_playback_time += dt
        return dt

    def reset(self):
        self._last_tick = time.time()
        self.total_playback_time = 0.0

    def set_fps(self, fps: float):
        if fps > 0:
            self.target_fps = fps
            self.frame_duration = 1.0 / fps
