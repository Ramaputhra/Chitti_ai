from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class VoiceProfile:
    voice_id: str
    name: str
    provider: str
    gender: str
    language: str
    sample_rate: int = 24000
    speed: float = 1.0
    pitch: float = 1.0
    stability: float = 0.75

class VoiceProfileManager:
    """
    S36A: Voice Profile Manager supporting default profiles and custom voice profiles.
    """
    DEFAULT_PROFILES: Dict[str, VoiceProfile] = {
        "prof_female": VoiceProfile("prof_female", "Professional Female", "SherpaONNX", "Female", "en-US", 24000, 1.0, 1.0),
        "friendly_female": VoiceProfile("friendly_female", "Friendly Female", "SherpaONNX", "Female", "en-US", 24000, 1.05, 1.0),
        "prof_male": VoiceProfile("prof_male", "Professional Male", "SherpaONNX", "Male", "en-US", 24000, 1.0, 0.95),
        "friendly_male": VoiceProfile("friendly_male", "Friendly Male", "SherpaONNX", "Male", "en-US", 24000, 1.05, 0.95),
        "robot": VoiceProfile("robot", "Robot", "SherpaONNX", "Neutral", "en-US", 16000, 0.9, 1.2),
        "narrator": VoiceProfile("narrator", "Narrator", "SherpaONNX", "Male", "en-US", 24000, 0.95, 0.9)
    }

    def __init__(self, active_profile_id: str = "friendly_female"):
        self._profiles = dict(self.DEFAULT_PROFILES)
        self._active_profile_id = active_profile_id if active_profile_id in self._profiles else "friendly_female"

    @property
    def active_profile(self) -> VoiceProfile:
        return self._profiles[self._active_profile_id]

    def set_active_profile(self, profile_id: str) -> bool:
        if profile_id in self._profiles:
            self._active_profile_id = profile_id
            return True
        return False

    def register_profile(self, profile: VoiceProfile):
        self._profiles[profile.voice_id] = profile

    def list_profiles(self) -> List[VoiceProfile]:
        return list(self._profiles.values())
