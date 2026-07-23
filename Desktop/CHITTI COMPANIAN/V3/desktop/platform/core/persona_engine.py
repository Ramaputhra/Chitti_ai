import logging
from desktop.models.presentation_models import (
    ResponseIntent, PresentationDecision, PresentationProfile, PresentationPriority
)

logger = logging.getLogger(__name__)

class PersonaEngine:
    """
    Applies the User Presentation Profile to the deterministic ResponseIntent.
    Enforces internal caps (e.g., humour <= 0.5) to maintain professional clarity.
    """
    def __init__(self, profile: PresentationProfile):
        self.profile = profile
        # Enforce architecture constraint on humour
        if self.profile.speech_persona.humour > 0.5:
            logger.warning("PersonaEngine: Humour capped at 0.5 internally.")
            self.profile.speech_persona.humour = 0.5

    def generate_decision(self, intent: ResponseIntent) -> PresentationDecision:
        logger.info(f"PersonaEngine: Generating presentation for {intent.message_key}")
        
        # In a real environment, this invokes a local LLM or templating engine.
        # Here we mock the behavior of applying the persona sliders.
        response_text = ""
        
        if intent.message_key == "folder.opened":
            if self.profile.speech_persona.humour > 0.1:
                response_text = "Downloads are open. Hopefully there aren't too many forgotten screenshots."
            elif self.profile.speech_persona.friendly > 0.1:
                response_text = "Done! I've opened your Downloads folder."
            else:
                response_text = "Execution verified. The Downloads folder has been opened."
        else:
            response_text = "Task completed."

        return PresentationDecision(
            response_text=response_text,
            language="en",
            voice=self.profile.voice,
            avatar_animation="joy" if intent.status == "SUCCESS" else "concern",
            expression=self.profile.animation_level,
            sound="success_chime.wav" if self.profile.sound_effects else None,
            followup_window=True, # Open follow-up window on completion
            expand_avatar=True,
            presentation_priority=PresentationPriority.NORMAL
        )
