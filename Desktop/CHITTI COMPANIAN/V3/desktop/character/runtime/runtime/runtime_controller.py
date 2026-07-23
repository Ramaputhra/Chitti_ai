import time
import logging
from typing import Optional
from desktop.character.behavior.script.behavior_script import BehaviorScript
from desktop.character.behavior.speech.speech_context import SpeechContext
from desktop.character.runtime.assets.asset_loader import AssetLoader
from desktop.character.runtime.player.clip_player import ClipPlayer
from desktop.character.runtime.player.behavior_timeline_player import BehaviorTimelinePlayer
from desktop.character.runtime.player.behavior_script_player import BehaviorScriptPlayer
from desktop.character.runtime.renderer.character_window import CharacterWindow
from desktop.character.runtime.metrics.playback_metrics import PlaybackMetrics
from desktop.character.runtime.renderer.overlay_renderer import DebugOverlayState

logger = logging.getLogger(__name__)

class RuntimeController:
    """
    S36B: Runtime Controller managing the playback engine loop, animation clock ticks, asset loading,
    and character window updates.
    """
    def __init__(self):
        self.asset_loader = AssetLoader()
        self.clip_player = ClipPlayer(self.asset_loader)
        self.timeline_player = BehaviorTimelinePlayer(self.clip_player)
        self.script_player = BehaviorScriptPlayer(self.timeline_player)
        self.window = CharacterWindow()
        self.metrics = PlaybackMetrics()
        self.is_running = False

    def start(self):
        self.is_running = True
        self.window.show()
        logger.info("[RuntimeController] Runtime Started.")

    def stop(self):
        self.is_running = False
        self.window.hide()
        logger.info("[RuntimeController] Runtime Stopped.")

    def execute_script(self, script: BehaviorScript, speech_context: Optional[SpeechContext] = None):
        if not self.is_running:
            self.start()
        self.script_player.play_script(script, speech_context)

    def tick(self, dt: float = 0.071) -> Optional[str]:  # ~14 FPS tick (0.071s)
        if not self.is_running:
            return None

        self.metrics.record_frame(dt)
        frame_path = self.script_player.update(dt)

        if self.window.debug_mode:
            current_behavior = "CHR_IDLE_001"
            frame_idx = 1
            if self.clip_player.current_clip:
                current_behavior = self.clip_player.current_clip.behavior_id
                frame_idx = self.clip_player.frame_player.current_frame_index + 1
                
            dbg = DebugOverlayState(
                behavior_id=current_behavior,
                frame_index=frame_idx,
                fps=self.metrics.current_fps,
                memory_mb=self.metrics.memory_mb,
                playback_time=self.metrics.total_playback_time,
                current_state=self.window.state.value
            )
            overlay_text = self.window.render_debug_overlay(dbg)
            logger.debug(f"\n{overlay_text}")

        return frame_path
