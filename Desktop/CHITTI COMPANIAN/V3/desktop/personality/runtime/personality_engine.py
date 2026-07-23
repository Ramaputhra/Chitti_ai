import logging
from typing import Tuple, List, Optional, Dict, Any
from desktop.personality.runtime.personality_profile_manager import PersonalityProfileManager
from desktop.personality.runtime.personality_state import PersonalityProfile
from desktop.personality.runtime.narration_style_engine import NarrationStyleEngine
from desktop.personality.runtime.narration_context import NarrationContext
from desktop.personality.runtime.speech_personality_adapter import SpeechPersonalityAdapter, VoicePersonalityParameters
from desktop.personality.runtime.behavior_personality_adapter import BehaviorPersonalityAdapter
from desktop.personality.runtime.ui_personality_adapter import UIPersonalityAdapter
from desktop.personality.runtime.personality_metrics import PersonalityMetrics

logger = logging.getLogger(__name__)

class PersonalityEngine:
    """
    S36A-R1: Master Personality Engine facade.
    The single canonical source of truth for Personality, Speaking Style, Humor, Friendliness,
    Formality, Empathy, Motivation, Conciseness, Talkativeness, Curiosity.
    Influences:
    1. Narration Composer
    2. Voice Runtime
    3. Behavior Scheduler
    4. Desktop UI wording
    """
    def __init__(self, storage_path: Optional[str] = None):
        self.profile_manager = PersonalityProfileManager(storage_path=storage_path)
        self.narration_engine = NarrationStyleEngine()
        self.speech_adapter = SpeechPersonalityAdapter()
        self.behavior_adapter = BehaviorPersonalityAdapter()
        self.ui_adapter = UIPersonalityAdapter()
        self.metrics = PersonalityMetrics()
        logger.info("PersonalityEngine Platform initialized cleanly.")

    @property
    def active_profile(self) -> PersonalityProfile:
        return self.profile_manager.active_profile

    def apply_preset(self, preset_key: str) -> bool:
        ok = self.profile_manager.apply_preset(preset_key)
        if ok:
            self.metrics.preset_apply_count += 1
            self.metrics.profile_change_count += 1
        return ok

    def update_traits(self, **traits) -> Tuple[bool, List[str]]:
        ok, errors = self.profile_manager.update_active_traits(**traits)
        if ok:
            self.metrics.profile_change_count += 1
        return ok, errors

    def rewrite_narration(self, text: str, context: Optional[NarrationContext] = None) -> str:
        self.metrics.narration_rewrites_count += 1
        return self.narration_engine.rewrite_narration(text, self.active_profile, context)

    def adapt_voice_parameters(self) -> VoicePersonalityParameters:
        self.metrics.voice_adaptation_count += 1
        return self.speech_adapter.adapt_voice_parameters(self.active_profile)

    def adapt_behavior_selection(self, base_behavior: str) -> str:
        self.metrics.behavior_adaptation_count += 1
        return self.behavior_adapter.adapt_behavior_selection(self.active_profile, base_behavior)

    def adapt_ui_text(self, key: str, default_text: str) -> str:
        self.metrics.ui_adaptation_count += 1
        return self.ui_adapter.adapt_ui_text(self.active_profile, key, default_text)

    def export_profile_json(self) -> str:
        return self.profile_manager.export_json()

    def import_profile_json(self, json_str: str) -> Tuple[bool, List[str]]:
        return self.profile_manager.import_json(json_str)
