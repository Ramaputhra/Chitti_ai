import logging
from typing import Tuple, Optional, Dict, Any
from desktop.character.behavior.speech.speech_context import SpeechTimeline
from desktop.voice.runtime.speech_runtime import SpeechRuntime
from desktop.voice.runtime.language_manager import LanguageManager
from desktop.voice.runtime.voice_profile_manager import VoiceProfileManager, VoiceProfile
from desktop.voice.runtime.speech_style_manager import SpeechStyleManager, SpeechStyle
from desktop.voice.runtime.pronunciation_manager import PronunciationManager
from desktop.voice.runtime.speech_session import SpeechSession

logger = logging.getLogger(__name__)

class VoiceRuntime:
    """
    S36A: Master Voice Runtime Platform facade owning Language Management, Voice Profiles,
    Speech Styles, Pronunciation, TTS, Speech Queue, Speech Sessions, Speech Timeline,
    Speech Events, and Speech Cache.
    Completely independent from Character Runtime, Presentation Platform, and Desktop UI Platform.
    """
    def __init__(self):
        self.speech_runtime = SpeechRuntime()
        self.language_manager = LanguageManager()
        self.profile_manager = VoiceProfileManager()
        self.style_manager = SpeechStyleManager()
        self.pronunciation_manager = PronunciationManager()
        logger.info("VoiceRuntime Platform initialized cleanly.")

    def set_language(self, lang_code: str) -> bool:
        return self.language_manager.set_language(lang_code)

    def set_voice_profile(self, profile_id: str) -> bool:
        return self.profile_manager.set_active_profile(profile_id)

    def set_speech_style(self, style_id: str) -> bool:
        return self.style_manager.set_active_style(style_id)

    def add_pronunciation(self, word: str, phonetic: str):
        self.pronunciation_manager.add_pronunciation(word, phonetic)

    def synthesize_text(
        self,
        text: str,
        speech_id: str = "sp_001",
        session_id: str = "sess_001",
        emotion_tag: str = "NEUTRAL"
    ) -> Tuple[SpeechSession, SpeechTimeline]:
        lang = self.language_manager.current_language
        voice_prof = self.profile_manager.active_profile.voice_id
        style = self.style_manager.active_style.name

        return self.speech_runtime.process_text_response(
            speech_id=speech_id,
            session_id=session_id,
            text=text,
            language=lang,
            voice_profile=voice_prof,
            style=style,
            emotion_tag=emotion_tag
        )

    def play_speech(self, session: SpeechSession):
        self.speech_runtime.play_speech_session(session)

    def stop_speech(self):
        self.speech_runtime.stop_speech_session()

    @property
    def metrics(self):
        return self.speech_runtime.metrics
