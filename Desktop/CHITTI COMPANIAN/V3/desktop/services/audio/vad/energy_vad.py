import numpy as np

from desktop.platform.shared.interfaces.vad import IVADStrategy


class EnergyVAD(IVADStrategy):
    """
    Calculates the Root Mean Square (RMS) energy of the audio chunk,
    with a dynamic noise floor to adapt to background static/fans.
    Includes an initial calibration phase to avoid getting permanently stuck.
    """
    def __init__(self) -> None:
        self.noise_floor = 0.01
        self.margin = 0.02
        self.alpha = 0.1  # Adaptation rate
        self.frames_processed = 0
        self.calibration_frames = 30  # Force adapt for the first ~2 seconds

    def initialize(self) -> None:
        pass

    def process_frame(self, audio_data: np.ndarray) -> bool:
        if len(audio_data) == 0:
            return False

        # Convert to float for normalized RMS calculation
        float_data = audio_data.astype(np.float32) / 32768.0
        rms = np.sqrt(np.mean(np.square(float_data)))
        
        self.frames_processed += 1
        
        # Force calibration for the first X frames
        if self.frames_processed < self.calibration_frames:
            self.noise_floor = (self.noise_floor * (1 - self.alpha)) + (rms * self.alpha)
            return False
            
        threshold = self.noise_floor + self.margin
        is_speech = rms > threshold
        
        # If it's silence, slowly adapt the noise floor to match background
        if not is_speech:
            self.noise_floor = (self.noise_floor * (1 - self.alpha)) + (rms * self.alpha)
            # Cap the noise floor to avoid it adapting to speech if margin is breached slowly
            self.noise_floor = min(self.noise_floor, 0.1)
            
        return bool(is_speech)
