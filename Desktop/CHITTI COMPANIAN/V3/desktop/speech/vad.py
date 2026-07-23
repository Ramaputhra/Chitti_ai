import numpy as np

class SileroVAD:
    """Wrapper around silero-vad to detect speech segments from continuous audio."""
    def __init__(self, threshold: float = 0.5, sampling_rate: int = 16000):
        self.threshold = threshold
        self.sampling_rate = sampling_rate
        # In production: self.model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')
        self._is_active = False

    def is_speech(self, audio_chunk: bytes) -> bool:
        """
        Takes raw audio bytes (16-bit PCM), converts to numpy, and runs VAD.
        Returns True if speech probability > threshold.
        """
        # Mock VAD logic: assumes any significant audio energy is speech
        try:
            audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
            if len(audio_data) == 0:
                return False
                
            # Basic energy threshold mock for Silero
            energy = np.mean(np.abs(audio_data))
            return energy > 500
        except Exception:
            return False
