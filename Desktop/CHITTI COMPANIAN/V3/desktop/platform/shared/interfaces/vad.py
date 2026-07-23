from typing import Protocol

import numpy as np


class IVADStrategy(Protocol):
    """
    Strategy pattern for Voice Activity Detection.
    Allows hot-swapping between Energy thresholds, WebRTC VAD, and Neural VADs.
    """
    def initialize(self) -> None:
        ...

    def process_frame(self, audio_data: np.ndarray) -> bool:
        """
        Analyzes a single chunk of audio.
        Returns True if speech is detected, False otherwise.
        """
        ...
