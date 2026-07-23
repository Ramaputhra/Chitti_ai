from dataclasses import dataclass
from desktop.personality.runtime.personality_state import PersonalityProfile

@dataclass
class VoicePersonalityParameters:
    speech_rate: float = 1.0
    pause_length: float = 1.0
    emphasis: float = 1.0
    intonation_level: float = 1.0
    expression_level: float = 1.0
    voice_energy: float = 1.0

class SpeechPersonalityAdapter:
    """
    S36A-R1: Maps PersonalityProfile traits to Voice Runtime speech parameters.
    Does NOT generate provider-specific SSML.
    """
    def adapt_voice_parameters(self, profile: PersonalityProfile) -> VoicePersonalityParameters:
        rate = 1.0 + (profile.talkative - 0.5) * 0.3 - (profile.patient - 0.5) * 0.2
        pause = 1.0 + (profile.patient - 0.5) * 0.4 - (profile.concise - 0.5) * 0.3
        emph = 1.0 + (profile.expressive - 0.5) * 0.4 + (profile.motivational - 0.5) * 0.3
        intonation = 1.0 + (profile.expressive - 0.5) * 0.5
        expression = 1.0 + (profile.friendly - 0.5) * 0.4 + (profile.playful - 0.5) * 0.4
        energy = 1.0 + (profile.motivational - 0.5) * 0.5 + (profile.confident - 0.5) * 0.3

        return VoicePersonalityParameters(
            speech_rate=round(max(0.7, min(1.5, rate)), 2),
            pause_length=round(max(0.5, min(2.0, pause)), 2),
            emphasis=round(max(0.8, min(1.8, emph)), 2),
            intonation_level=round(max(0.7, min(1.8, intonation)), 2),
            expression_level=round(max(0.6, min(1.8, expression)), 2),
            voice_energy=round(max(0.6, min(1.8, energy)), 2)
        )
