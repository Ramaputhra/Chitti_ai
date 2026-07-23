import os
import time
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class ConversationLogger:
    def __init__(self, event_bus: Any, log_dir: str = "desktop/logs"):
        self.event_bus = event_bus
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "conversation.log")
        
        self.current_session: Dict[str, Any] = {}
        
        if hasattr(self.event_bus, "subscribe"):
            self.event_bus.subscribe("WAKE_WORD_DETECTED", self._on_wake)
            self.event_bus.subscribe("TRANSCRIBE_BUFFER", self._on_transcribe_start)
            self.event_bus.subscribe("USER_TRANSCRIPT_GENERATED", self._on_transcript)
            self.event_bus.subscribe("InferenceStarted", self._on_inference_start)
            self.event_bus.subscribe("InferenceCompleted", self._on_inference_complete)
            self.event_bus.subscribe("TTS_STARTED", self._on_tts_start)
            self.event_bus.subscribe("TTS_FINISHED", self._on_tts_finish)
            self.event_bus.subscribe("SPEECH_STATE_CHANGED", self._on_state_changed)

    def _on_wake(self, event_data: Any):
        self.current_session = {
            "start_time": time.time(),
            "start_dt": datetime.now(),
            "transcript": None,
            "response": None,
            "stt_start": None,
            "stt_duration": 0,
            "llm_start": None,
            "llm_duration": 0,
            "tts_start": None,
            "tts_duration": 0,
            "completed": False
        }

    def _on_transcribe_start(self, event_data: Any):
        if self.current_session:
            self.current_session["stt_start"] = time.time()

    def _on_transcript(self, event_data: Any):
        if self.current_session:
            payload = getattr(event_data, "payload", event_data.get("payload", {}) if isinstance(event_data, dict) else {})
            self.current_session["transcript"] = payload.get("text", "")
            if self.current_session.get("stt_start"):
                self.current_session["stt_duration"] = time.time() - self.current_session["stt_start"]

    def _on_inference_start(self, event_data: Any):
        if self.current_session:
            self.current_session["llm_start"] = time.time()

    def _on_inference_complete(self, event_data: Any):
        if self.current_session:
            payload = getattr(event_data, "payload", event_data.get("payload", {}) if isinstance(event_data, dict) else {})
            self.current_session["response"] = payload.get("response", "")
            if self.current_session.get("llm_start"):
                self.current_session["llm_duration"] = time.time() - self.current_session["llm_start"]

    def _on_tts_start(self, event_data: Any):
        if self.current_session:
            self.current_session["tts_start"] = time.time()

    def _on_tts_finish(self, event_data: Any):
        if self.current_session and not self.current_session.get("completed"):
            if self.current_session.get("tts_start"):
                self.current_session["tts_duration"] = time.time() - self.current_session["tts_start"]
            self._finalize_log()

    def _on_state_changed(self, event_data: Any):
        payload = getattr(event_data, "payload", event_data.get("payload", {}) if isinstance(event_data, dict) else {})
        state = payload.get("state")
        if state == "SLEEPING" and self.current_session and not self.current_session.get("completed"):
            self._finalize_log()

    def _finalize_log(self):
        if not self.current_session or self.current_session.get("completed"):
            return
            
        self.current_session["completed"] = True
        
        total_duration = time.time() - self.current_session["start_time"]
        
        def format_ms(seconds):
            if seconds < 1.0:
                return f"{int(seconds * 1000)} ms"
            return f"{seconds:.2f} s"

        dt_str = self.current_session["start_dt"].strftime("%H:%M:%S")
        user_text = self.current_session.get("transcript") or "<empty>"
        response_text = self.current_session.get("response") or "<no response>"
        
        log_block = f"""
[{dt_str}]
Wake

User:
{user_text}

Whisper:
{format_ms(self.current_session.get('stt_duration', 0))}

LLM:
{format_ms(self.current_session.get('llm_duration', 0))}

Piper:
{format_ms(self.current_session.get('tts_duration', 0))}

Response:
{response_text}

Conversation Total:
{format_ms(total_duration)}
----------------------------------------"""
        
        print(f"\n{log_block}\n")
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_block + "\n")
        except Exception as e:
            logger.error(f"Failed to write conversation log: {e}")
