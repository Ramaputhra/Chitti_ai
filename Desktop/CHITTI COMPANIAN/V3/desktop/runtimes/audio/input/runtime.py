import os
import time
import threading
import logging
from typing import Any, Optional

import sounddevice as sd
import webrtcvad
import numpy as np

# We will import openwakeword dynamically so the script doesn't crash if it's missing
# from openwakeword.model import Model

from desktop.platform.shared.interfaces.event_bus import Event

logger = logging.getLogger(__name__)

class AudioInputRuntime:
    """
    Owns the microphone, Wake Word Detection, VAD, and Echo Protection.
    Publishes to the EventBus so SpeechOrchestrator can handle state transitions.
    """
    def __init__(self, event_bus: Any):
        self.event_bus = event_bus
        
        self.oww_model = None
        self.vad = None
        self.stream = None
        
        self._running = False
        self._mic_thread = None
        
        self._echo_suspended = False
        self._is_listening = False
        
        self._speech_buffer = bytearray()
        self._silence_frames = 0
        self._speech_frames = 0
        
        # Audio Config
        self.rate = 16000
        self.channels = 1
        self.chunk_size = 1280 # OpenWakeWord prefers 1280 (80ms at 16kHz)
        
        # VAD Config
        self.vad_aggressiveness = 3
        
        # Timing thresholds
        self.min_speech_frames = int(0.3 * self.rate / self.chunk_size)  # 300ms
        self.silence_timeout_frames = int(0.7 * self.rate / self.chunk_size) # 700ms
        self.max_frames = int(10.0 * self.rate / self.chunk_size) # 10s
        
        # Subscriptions
        if hasattr(self.event_bus, "subscribe"):
            self.event_bus.subscribe("TTS_STARTED", self._on_tts_started)
            self.event_bus.subscribe("TTS_FINISHED", self._on_tts_finished)
            self.event_bus.subscribe("SPEECH_STATE_CHANGED", self._on_state_changed)

    def start(self):
        try:
            from openwakeword.model import Model
            
            # Load default models (e.g. "hey_mycroft" or "alexa")
            # We'll use "alexa" as a fallback since it's built-in
            self.oww_model = Model(wakeword_models=["alexa"])
            
            self.vad = webrtcvad.Vad(self.vad_aggressiveness)
            
            self.stream = sd.RawInputStream(
                samplerate=self.rate,
                blocksize=self.chunk_size,
                dtype='int16',
                channels=self.channels
            )
            self.stream.start()
            
            self._running = True
            self._mic_thread = threading.Thread(target=self._process_microphone, daemon=True)
            self._mic_thread.start()
            logger.info("AudioInputRuntime started successfully (Wake word: Alexa).")
            
        except Exception as e:
            logger.error(f"Failed to start AudioInputRuntime: {e}")

    def stop(self):
        self._running = False
        if self._mic_thread:
            self._mic_thread.join(timeout=1.0)
            
        if self.stream:
            self.stream.stop()
            self.stream.close()
            
        logger.info("AudioInputRuntime stopped.")

    def _process_microphone(self):
        while self._running:
            try:
                pcm, overflow = self.stream.read(self.chunk_size)
                pcm_bytes = bytes(pcm)
                
                # Echo Protection (Mute Mic)
                if self._echo_suspended:
                    continue
                    
                import struct
                # Convert back to numpy array of int16 for openwakeword
                pcm_np = np.frombuffer(pcm_bytes, dtype=np.int16)
                
                # 1. Wake Word Detection (if not already listening)
                if not self._is_listening:
                    prediction = self.oww_model.predict(pcm_np)
                    # prediction is a dict: {'alexa': 0.1, ...}
                    for model_name, score in prediction.items():
                        if score > 0.5:  # threshold
                            logger.info(f"Wake word '{model_name}' detected! Score: {score}")
                            if hasattr(self.event_bus, "publish"):
                                self.event_bus.publish(Event("WAKE_WORD_DETECTED", source="AudioInputRuntime", payload={"model": "openwakeword"}))
                            # Clear buffer so it doesn't immediately trigger again
                            self.oww_model.reset()
                            break
                
                # 2. VAD and Buffering (if currently listening)
                else:
                    # Webrtc VAD requires exactly 10, 20, or 30ms frames
                    frame_len = int(16000 * 0.03 * 2) # 30ms at 16kHz, 16-bit = 960 bytes
                    is_speech = False
                    
                    # Check each 30ms chunk in the 80ms buffer
                    for i in range(0, len(pcm_bytes) - frame_len + 1, frame_len):
                        chunk = pcm_bytes[i:i+frame_len]
                        if len(chunk) == frame_len and self.vad.is_speech(chunk, self.rate):
                            is_speech = True
                            break
                            
                    if is_speech:
                        self._silence_frames = 0
                        self._speech_frames += 1
                        if not hasattr(self, '_speech_started') or not self._speech_started:
                            self._speech_started = True
                            if hasattr(self.event_bus, "publish"):
                                self.event_bus.publish(Event("SPEECH_STARTED", source="AudioInputRuntime", payload={}))
                    else:
                        self._silence_frames += 1
                        
                    self._speech_buffer.extend(pcm_bytes)
                    
                    # Check constraints
                    total_frames = self._speech_frames + self._silence_frames
                    
                    # Case A: User started speaking, then stopped
                    if getattr(self, '_speech_started', False) and self._silence_frames >= self.silence_timeout_frames:
                        # Finished speaking
                        logger.info(f"Speech captured. Length: {len(self._speech_buffer)} bytes")
                        if hasattr(self.event_bus, "publish"):
                            self.event_bus.publish(Event("SPEECH_STOPPED", source="AudioInputRuntime", payload={"buffer": bytes(self._speech_buffer)}))
                        self._is_listening = False
                        self._speech_buffer.clear()
                        self._silence_frames = 0
                        self._speech_frames = 0
                        self._speech_started = False
                        
                    # Case B: Max duration reached
                    elif total_frames >= self.max_frames:
                        logger.info(f"Max speech duration reached. Length: {len(self._speech_buffer)} bytes")
                        if hasattr(self.event_bus, "publish"):
                            self.event_bus.publish(Event("SPEECH_STOPPED", source="AudioInputRuntime", payload={"buffer": bytes(self._speech_buffer)}))
                        self._is_listening = False
                        self._speech_buffer.clear()
                        self._silence_frames = 0
                        self._speech_frames = 0
                        self._speech_started = False
                        
                    # Case C: Wake word detected but user never started speaking (timeout after 5s)
                    elif not getattr(self, '_speech_started', False) and self._silence_frames >= (5.0 * self.rate / self.chunk_size):
                        logger.info("Wake word timeout. User didn't say anything.")
                        self._is_listening = False
                        
                        buffer_copy = bytes(self._speech_buffer)
                        self._speech_buffer.clear()
                        self._silence_frames = 0
                        self._speech_frames = 0
                        if hasattr(self.event_bus, "publish"):
                            self.event_bus.publish(Event("SPEECH_STOPPED", source="AudioInputRuntime", payload={"buffer": buffer_copy}))
                            
            except Exception as e:
                logger.error(f"Error in microphone loop: {e}")
                time.sleep(0.1)

    # --- Event Handlers ---
    def _on_tts_started(self, event_data: Any):
        self._echo_suspended = True
        logger.debug("Mic muted (Echo Protection)")

    def _on_tts_finished(self, event_data: Any):
        self._echo_suspended = False
        logger.debug("Mic unmuted")
        
    def _on_state_changed(self, event_data: Any):
        payload = getattr(event_data, "payload", {})
        if isinstance(event_data, dict):
            payload = event_data.get("payload", {})
            
        state = payload.get("state")
        if state == "LISTENING":
            self._is_listening = True
            self._speech_buffer.clear()
            self._silence_frames = 0
            self._speech_frames = 0
        elif state == "SLEEPING":
            self._is_listening = False
