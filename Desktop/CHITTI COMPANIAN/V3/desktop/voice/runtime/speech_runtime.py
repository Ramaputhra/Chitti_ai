import time
import logging
from typing import Optional, Tuple
from desktop.character.behavior.speech.speech_context import SpeechTimeline
from desktop.voice.runtime.speech_session import SpeechSession, SpeechSessionState
from desktop.voice.runtime.speech_queue import SpeechQueue
from desktop.voice.runtime.speech_cache import SpeechCache
from desktop.voice.runtime.speech_metrics import SpeechMetrics
from desktop.voice.runtime.tts_manager import TTSManager
from desktop.voice.runtime.emotion_markup_engine import EmotionMarkupEngine
from desktop.voice.runtime.narration_composer import NarrationComposer
from desktop.voice.runtime.pronunciation_manager import PronunciationManager
from desktop.voice.runtime.speech_events import SpeechCreated, SpeechQueued, SpeechStarted, SpeechCompleted, SpeechInterrupted

logger = logging.getLogger(__name__)

class SpeechRuntime:
    """
    S36A: Core Speech Runtime Engine orchestrating speech queue, cache, composition, markup, and TTS synthesis.
    """
    def __init__(self):
        self.queue = SpeechQueue()
        self.cache = SpeechCache()
        self.metrics = SpeechMetrics()
        self.tts_manager = TTSManager()
        self.composer = NarrationComposer()
        self.markup_engine = EmotionMarkupEngine()
        self.pronunciation_mgr = PronunciationManager()
        self.active_session: Optional[SpeechSession] = None

    def process_text_response(
        self,
        speech_id: str,
        session_id: str,
        text: str,
        language: str = "en-US",
        voice_profile: str = "friendly_female",
        style: str = "Friendly",
        emotion_tag: str = "NEUTRAL"
    ) -> Tuple[SpeechSession, SpeechTimeline]:
        t0 = time.time()
        
        # 1. Apply pronunciation dictionary
        phonetic_text = self.pronunciation_mgr.apply_pronunciation(text)

        # 2. Composition & Markup
        narration = self.composer.compose_narration(phonetic_text, emotion_hint=emotion_tag, style_hint=style)
        markup = self.markup_engine.process_markup(narration.normalized_text, emotion_tag=emotion_tag)

        # 3. Check Cache
        cached = self.cache.get(narration.normalized_text, voice_profile)
        if cached:
            audio_path, timeline = cached
            session = SpeechSession(
                speech_id=speech_id,
                session_id=session_id,
                text_narration=text,
                language=language,
                voice_profile=voice_profile,
                speech_style=style,
                state=SpeechSessionState.READY,
                audio_path=audio_path,
                duration_seconds=timeline.total_duration
            )
            self.metrics.record_cache_hit()
            logger.info(f"[SpeechRuntime] Cache HIT for speech_id='{speech_id}'")
            return session, timeline

        self.metrics.record_cache_miss()

        # 4. Create & Synthesize SpeechSession
        session = SpeechSession(
            speech_id=speech_id,
            session_id=session_id,
            text_narration=text,
            language=language,
            voice_profile=voice_profile,
            speech_style=style,
            state=SpeechSessionState.CREATED,
            created_at=t0
        )

        audio_path, timeline = self.tts_manager.synthesize_speech(session, markup=markup)
        
        # Put into Cache
        self.cache.put(text, voice_profile, speech_id, audio_path, timeline)
        
        synth_time = (time.time() - t0) * 1000
        self.metrics.record_synthesis(synthesis_ms=synth_time, latency_ms=synth_time)

        return session, timeline

    def play_speech_session(self, session: SpeechSession):
        if self.active_session and self.active_session.state == SpeechSessionState.PLAYING:
            logger.info(f"[SpeechRuntime] Interrupting speech_id='{self.active_session.speech_id}'")
            self.active_session.state = SpeechSessionState.CANCELLED
            
        self.active_session = session
        session.state = SpeechSessionState.PLAYING
        logger.info(f"[SpeechRuntime] Playing speech_id='{session.speech_id}' (Duration: {session.duration_seconds}s)")

    def stop_speech_session(self):
        if self.active_session:
            self.active_session.state = SpeechSessionState.COMPLETED
            self.active_session = None
