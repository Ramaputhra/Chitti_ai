import logging
from typing import Optional
from desktop.character.runtime.player.frame_player import FramePlayer
from desktop.character.runtime.assets.asset_loader import AssetLoader, LoadedBehaviorClip
from desktop.character.runtime.audio.sound_effect_player import SoundEffectPlayer

logger = logging.getLogger(__name__)

class ClipPlayer:
    """
    S36B: Clip Player layer playing individual 2D PNG behavior clips with sound effects.
    """
    def __init__(self, asset_loader: AssetLoader):
        self.asset_loader = asset_loader
        self.frame_player = FramePlayer()
        self.sound_player = SoundEffectPlayer()
        self.current_clip: Optional[LoadedBehaviorClip] = None

    def play_clip(self, behavior_id_or_name: str) -> bool:
        clip = self.asset_loader.load_clip(behavior_id_or_name)
        if not clip:
            return False

        self.current_clip = clip
        self.frame_player.load_clip(clip)
        self.frame_player.play()
        self.sound_player.play_sound(clip.sound_path)
        logger.info(f"[ClipPlayer] Playing clip '{clip.behavior_id}' ({len(clip.frame_paths)} frames)")
        return True

    def update(self, dt: float) -> Optional[str]:
        return self.frame_player.update(dt)

    def stop(self):
        self.frame_player.stop()
        self.current_clip = None
