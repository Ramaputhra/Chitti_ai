import logging
from typing import Optional
from desktop.models.presentation_models import PresentationDecision

logger = logging.getLogger(__name__)

class ExpressionAdapter:
    """
    Bridge to Avatar and Piper TTS. Contains no business logic.
    """
    def play_sound(self, sound_file: str) -> None:
        logger.info(f"ExpressionAdapter: PLAY SOUND [{sound_file}]")

    def animate_avatar(self, animation: str) -> None:
        logger.info(f"ExpressionAdapter: AVATAR ANIMATION [{animation}]")

    def speak(self, text: str, voice: str) -> None:
        logger.info(f"ExpressionAdapter: TTS (Piper) [{voice}]: \"{text}\"")
        
    def stop_speaking(self) -> None:
        logger.info("ExpressionAdapter: TTS STOPPED")

    def present_decision(self, decision: PresentationDecision) -> None:
        """
        Executes the exact decision. Respects Rule 42 (Animation > Sound > Speech).
        """
        if decision.avatar_animation:
            self.animate_avatar(decision.avatar_animation)
            
        if decision.sound:
            self.play_sound(decision.sound)
            
        if decision.response_text:
            # Rule 41: Speech exists only when it adds information
            # We assume the PersonaEngine evaluated this before providing text
            self.speak(decision.response_text, decision.voice)
