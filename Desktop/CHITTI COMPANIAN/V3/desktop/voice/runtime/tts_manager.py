import time
import os
import wave
import struct
import logging
from typing import Optional, Dict, Any, Tuple
from desktop.character.behavior.speech.speech_context import SpeechTimeline
from desktop.voice.runtime.speech_session import SpeechSession, SpeechSessionState
from desktop.voice.runtime.speech_timeline_builder import SpeechTimelineBuilder
from desktop.voice.runtime.emotion_markup_engine import SpeechMarkupMetadata

logger = logging.getLogger(__name__)

class MockTTSProvider:
    """
    S36A: Mock TTS Provider synthesizing audio WAV files and generating SpeechTimeline.
    """
    def synthesize(self, text: str, voice_profile: str, output_dir: str, speech_id: str) -> Tuple[str, float]:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{speech_id}.wav")
        
        words = len(text.split())
        duration = max(1.0, round(words * 0.3, 2))
        
        sample_rate = 16000
        n_samples = int(sample_rate * min(1.0, duration))
        
        with wave.open(filepath, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            data = bytearray()
            for i in range(n_samples):
                val = int(300 * (i % 20 < 10))
                data.extend(struct.pack('<h', val))
            wav_file.writeframes(data)
            
        return filepath, duration

class TTSManager:
    """
    S36A: TTS Manager managing providers, synthesis queue, audio generation, SpeechTimeline creation,
    SpeechSession lifecycle, cancellation, and interruption.
    """
    def __init__(self, provider_name: str = "SherpaONNX"):
        self.provider_name = provider_name
        self.mock_provider = MockTTSProvider()
        self.builder = SpeechTimelineBuilder()

    def synthesize_speech(
        self,
        session: SpeechSession,
        markup: Optional[SpeechMarkupMetadata] = None,
        output_dir: str = "temp_audio"
    ) -> Tuple[str, SpeechTimeline]:
        t0 = time.time()
        session.state = SpeechSessionState.SYNTHESIZING
        
        audio_path, duration = self.mock_provider.synthesize(
            text=session.text_narration,
            voice_profile=session.voice_profile,
            output_dir=output_dir,
            speech_id=session.speech_id
        )

        timeline = self.builder.build_timeline(
            speech_id=session.speech_id,
            audio_id=f"audio_{session.speech_id}",
            duration=duration,
            language=session.language,
            voice_profile=session.voice_profile,
            style=session.speech_style,
            markup=markup,
            provider=self.provider_name,
            audio_path=audio_path
        )

        session.audio_path = audio_path
        session.duration_seconds = duration
        session.state = SpeechSessionState.READY

        logger.info(f"[TTSManager] Synthesized speech_id='{session.speech_id}' in {(time.time()-t0)*1000:.1f}ms. Duration: {duration}s")
        return audio_path, timeline
