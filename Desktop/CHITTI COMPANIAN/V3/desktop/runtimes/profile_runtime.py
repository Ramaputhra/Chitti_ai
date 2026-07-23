import logging
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from desktop.models.lifecycle import IRuntime, HealthState
from desktop.app.context import KernelContext
from desktop.models.profile import UserProfile, UserIdentity, AdaptivePreferences, VoiceProfile, ExperienceProfile

logger = logging.getLogger(__name__)

class ProfileRuntime(IRuntime):
    """
    Manages the UserProfile defining WHO the user is.
    Follows Rule 263: Configuration Ownership.
    Loads from AppData/CHITTI/profile/profile.json.
    """
    def __init__(self, config_dir: str = "AppData/CHITTI/profile"):
        self.context: Optional[KernelContext] = None
        self._running = False
        self._config_dir = config_dir
        
        # Initialize default profile
        self._profile = UserProfile(
            identity=UserIdentity(
                name="Boss",
                role="User",
                languages=["en"],
                timezone="UTC",
                explicit_preferences=[],
                declared_goals=[]
            ),
            adaptive_preferences=AdaptivePreferences(traits={}, evidence={}),
            revisions=[],
            voice=VoiceProfile(),
            experience=ExperienceProfile()
        )
        self._profile_file = os.path.join(self._config_dir, "profile.json")

    @property
    def dependencies(self) -> List[Any]:
        return []

    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        if not os.path.exists(self._config_dir):
            try:
                os.makedirs(self._config_dir, exist_ok=True)
            except Exception as e:
                logger.warning(f"Could not create profile dir: {e}")
        return True

    async def start(self) -> bool:
        self._running = True
        self.reload_profile()
        logger.info("ProfileRuntime started.")
        return True

    async def stop(self) -> bool:
        self._running = False
        return True

    def health(self) -> HealthState:
        return HealthState.HEALTHY

    async def shutdown(self) -> bool:
        return True

    def reload_profile(self):
        """Hot reloads profile from disk."""
        if os.path.exists(self._profile_file):
            try:
                with open(self._profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if "voice" in data:
                        v_data = data["voice"]
                        self._profile.voice.preferred_voice = v_data.get("preferred_voice", "default_en")
                        self._profile.voice.speed = v_data.get("speed", 1.0)
                        self._profile.voice.pitch = v_data.get("pitch", 1.0)
                        self._profile.voice.volume = v_data.get("volume", 1.0)
                        
                    if "experience" in data:
                        e_data = data["experience"]
                        self._profile.experience.morning_briefing_enabled = e_data.get("morning_briefing_enabled", True)
                        self._profile.experience.workspace_suggestions_enabled = e_data.get("workspace_suggestions_enabled", True)
                        self._profile.experience.proactive_suggestions_enabled = e_data.get("proactive_suggestions_enabled", False)
                        
                    logger.info("Profile hot reloaded from disk.")
            except Exception as e:
                logger.error(f"Failed to load profile.json: {e}")
        else:
            self.save_profile() # Create default

    def save_profile(self):
        """Persists current profile to disk."""
        if not os.path.exists(self._config_dir):
            return
        try:
            with open(self._profile_file, 'w', encoding='utf-8') as f:
                data = {
                    "voice": {
                        "preferred_voice": self._profile.voice.preferred_voice,
                        "speed": self._profile.voice.speed,
                        "pitch": self._profile.voice.pitch,
                        "volume": self._profile.voice.volume
                    },
                    "experience": {
                        "morning_briefing_enabled": self._profile.experience.morning_briefing_enabled,
                        "workspace_suggestions_enabled": self._profile.experience.workspace_suggestions_enabled,
                        "proactive_suggestions_enabled": self._profile.experience.proactive_suggestions_enabled
                    }
                }
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save profile.json: {e}")

    @property
    def current(self) -> UserProfile:
        return self._profile
