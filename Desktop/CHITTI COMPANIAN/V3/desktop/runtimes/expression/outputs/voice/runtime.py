import threading
import queue
import logging
from typing import Any

from desktop.platform.shared.interfaces.event_bus import IEventBus
from desktop.runtimes.expression.outputs.voice.events import (
    SpeakRequested, AudioStarted, AudioFinished, SpeakCompleted, SpeakInterrupted
)
from desktop.services.audio.speech_synth_router import SpeechSynthRouter

logger = logging.getLogger(__name__)

class VoiceRuntime:
    """
    Manages dynamic TTS audio playback and interruption logic (Rule 44).
    """
    def __init__(self, event_bus: IEventBus, speech_router: SpeechSynthRouter):
        self.event_bus = event_bus
        self.speech_router = speech_router
        self._playback_queue: queue.Queue = queue.Queue()
        
        self._is_playing = False
        self._should_stop = False
        self._playback_thread = None
        self._current_text = None
        
        if hasattr(self.event_bus, "subscribe"):
            self.event_bus.subscribe("Voice.SpeakRequested", self._on_speak_requested)
            self.event_bus.subscribe("Presence.StateChanged", self._on_presence_changed)

    def start(self):
        logger.info("VoiceRuntime started.")

    def stop(self):
        self._stop_playback()
        logger.info("VoiceRuntime stopped.")

    def _on_speak_requested(self, event: SpeakRequested):
        """Handle a request to speak text."""
        # Rule 44: Exclusive Voice Focus. Cancel any existing speech immediately.
        self._stop_playback(reason="new_focus")
        
        self._current_text = event.text
        self._should_stop = False
        self._is_playing = True
        
        # Start synthesis in a background thread so we don't block the event bus
        threading.Thread(target=self._synthesize_and_play, args=(event.text,), daemon=True).start()

    def _on_presence_changed(self, event: Any):
        """Interrupt speech if Presence shifts to LISTENING or OFFLINE (Rule 44)."""
        if event.current.name in ("LISTENING", "OFFLINE", "ERROR", "GOODBYE"):
            self._stop_playback(reason=f"presence_shift_{event.current.name}")

    def _stop_playback(self, reason: str = "interrupted"):
        if self._is_playing or self._playback_thread:
            logger.info(f"Interrupting voice playback: {reason}")
            self._should_stop = True
            self._is_playing = False
            
            # Flush queue
            while not self._playback_queue.empty():
                try:
                    self._playback_queue.get_nowait()
                except queue.Empty:
                    break
                    
            if hasattr(self.event_bus, "publish"):
                self.event_bus.publish(SpeakInterrupted(reason=reason))

    def _synthesize_and_play(self, text: str):
        """Background thread to synthesize stream and push to sounddevice."""
        try:
            import sounddevice as sd
            import numpy as np
            import time
            
            first_chunk = True
            
            # Pull stream from SpeechRouter
            for chunk_bytes in self.speech_router.synthesize_stream(text):
                if self._should_stop:
                    break
                    
                if first_chunk:
                    if hasattr(self.event_bus, "publish"):
                        self.event_bus.publish(AudioStarted())
                    first_chunk = False
                    
                # Convert bytes to numpy array
                audio_array = np.frombuffer(chunk_bytes, dtype=np.int16)
                
                # Start playback
                sd.play(audio_array, samplerate=22050)
                
                # Wait for playback to finish, but allow interruption
                duration = len(audio_array) / 22050.0
                elapsed = 0
                while elapsed < duration:
                    if self._should_stop:
                        sd.stop()
                        break
                    sleep_time = min(0.05, duration - elapsed)
                    time.sleep(sleep_time)
                    elapsed += sleep_time
                    
            if not self._should_stop:
                self._is_playing = False
                if hasattr(self.event_bus, "publish"):
                    self.event_bus.publish(AudioFinished())
                    self.event_bus.publish(SpeakCompleted())
                    
        except Exception as e:
            logger.error(f"Error during Voice playback: {e}")
            self._is_playing = False
            self._should_stop = False
