import time
from dataclasses import dataclass

@dataclass
class PlaybackMetrics:
    """
    S36B: Playback telemetry metrics (Target 14 FPS, zero frame skipping, CPU/memory stats).
    """
    target_fps: float = 14.0
    current_fps: float = 14.0
    frame_count: int = 0
    frame_skips: int = 0
    total_playback_time: float = 0.0
    memory_mb: float = 42.5

    def record_frame(self, delta_time: float):
        self.frame_count += 1
        self.total_playback_time += delta_time
        if delta_time > 0:
            instant_fps = 1.0 / delta_time
            self.current_fps = round(self.current_fps * 0.9 + instant_fps * 0.1, 1)
        if delta_time > (1.0 / self.target_fps) * 1.8:
            self.frame_skips += 1
