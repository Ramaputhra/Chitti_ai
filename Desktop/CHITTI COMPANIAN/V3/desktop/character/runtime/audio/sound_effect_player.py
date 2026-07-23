import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SoundEffectPlayer:
    """
    S36B: Sound Effect Player playing sound.wav associated with behavior clips.
    """
    def play_sound(self, sound_path: Optional[str]):
        if sound_path and os.path.exists(sound_path):
            logger.info(f"[SoundEffectPlayer] Playing sound effect: {os.path.basename(sound_path)}")
