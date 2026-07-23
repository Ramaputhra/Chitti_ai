from dataclasses import dataclass

@dataclass
class PersonalityMetrics:
    """
    S36A-R1: Telemetry metrics for Personality Engine adaptations.
    """
    profile_change_count: int = 0
    preset_apply_count: int = 0
    narration_rewrites_count: int = 0
    voice_adaptation_count: int = 0
    behavior_adaptation_count: int = 0
    ui_adaptation_count: int = 0
