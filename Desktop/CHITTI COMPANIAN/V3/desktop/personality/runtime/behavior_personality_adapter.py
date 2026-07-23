from desktop.personality.runtime.personality_state import PersonalityProfile

class BehaviorPersonalityAdapter:
    """
    S36A-R1: Maps PersonalityProfile traits to behavior selection preferences in Behavior Scheduler.
    - Professional -> TalkingProfessional
    - Friendly -> TalkingHappy / GreetingMorning
    - Empathetic -> TalkingConcern
    - Humorous -> TalkingPlayful
    """
    def adapt_behavior_selection(self, profile: PersonalityProfile, base_behavior: str) -> str:
        if profile.professional > 0.8:
            if base_behavior == "TalkingExplain":
                return "TalkingProfessional"
        if profile.friendly > 0.8:
            if base_behavior == "TalkingNeutral":
                return "TalkingHappy"
        if profile.empathetic > 0.8:
            if base_behavior == "Warning":
                return "TalkingConcern"
        if profile.humorous > 0.7:
            if base_behavior == "Smile":
                return "TalkingPlayful"
        return base_behavior
