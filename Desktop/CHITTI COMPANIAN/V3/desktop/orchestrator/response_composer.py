import queue
import threading
from typing import Any
from desktop.orchestrator.response_packet import ResponsePacket

class StreamingState:
    QUEUED = "QUEUED"
    STREAMING = "STREAMING"
    PAUSED = "PAUSED"
    INTERRUPTED = "INTERRUPTED"
    COMPLETED = "COMPLETED"

class ResponseComposer:
    def __init__(self, tts_renderer, ui_renderer, character_renderer):
        self.tts_renderer = tts_renderer
        self.ui_renderer = ui_renderer
        self.character_renderer = character_renderer
        self.packet_queue = queue.Queue()
        self.current_state = StreamingState.COMPLETED
        self._thread = None
        self._running = False

    def start(self):
        self._running = True
        self.current_state = StreamingState.COMPLETED
        self._thread = threading.Thread(target=self._render_loop, daemon=True, name="ResponseComposerThread")
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        self.current_state = StreamingState.INTERRUPTED

    def interrupt(self):
        self.packet_queue.queue.clear()
        self.current_state = StreamingState.INTERRUPTED

    def compose(self, execution_result: Any) -> ResponsePacket:
        status = getattr(execution_result, "overall_status", "UNKNOWN")
        text = "Task processing completed." if status == "COMPLETED" else "Task encountered an error."
        emotion = "Confident" if status == "COMPLETED" else "Uncertain"
        animation = "Nod/Smile" if status == "COMPLETED" else "Thinking/Apologizing"
        
        packet = ResponsePacket(
            text=text,
            emotion=emotion,
            animation=animation
        )
        self.packet_queue.put(packet)
        self.current_state = StreamingState.QUEUED
        return packet

    def _render_loop(self):
        while self._running:
            try:
                packet = self.packet_queue.get(timeout=0.1)
                self.current_state = StreamingState.STREAMING
                try:
                    if self.ui_renderer: self.ui_renderer.update(packet.ui_metadata)
                    if self.character_renderer: self.character_renderer.set_animation(packet.animation)
                    if self.tts_renderer: self.tts_renderer.play(packet.text, packet.audio_metadata)
                    self.current_state = StreamingState.COMPLETED
                except Exception as e:
                    print(f"[RENDER_ERROR] Fallback triggered. Reason: {e}")
                    self.current_state = StreamingState.COMPLETED
            except queue.Empty:
                pass
