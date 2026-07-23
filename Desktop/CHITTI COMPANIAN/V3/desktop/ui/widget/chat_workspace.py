import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal, Slot
from desktop.platform.shared.interfaces.event_bus import Event
from typing import Any

logger = logging.getLogger(__name__)

class ChatWorkspace(QWidget):
    """
    Conversation Inspector UI (Sprint 22).
    Shows conversation timeline, intents, and capabilities.
    Subscribes to EventBus for data, does not own conversation state.
    """
    # Signals for thread-safe UI updates
    append_text_signal = Signal(str)

    def __init__(self, event_bus: Any, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self.setWindowTitle("CHITTI Chat Workspace")
        self.resize(500, 700)
        
        self.layout = QVBoxLayout(self)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type a message...")
        self.text_input.returnPressed.connect(self._on_send)
        input_layout.addWidget(self.text_input)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._on_send)
        input_layout.addWidget(self.send_button)
        
        self.layout.addLayout(input_layout)
        
        self.append_text_signal.connect(self._append_text)
        
        self._subscribe_events()

    def _subscribe_events(self):
        if not hasattr(self.event_bus, "subscribe"):
            return
            
        self.event_bus.subscribe("ConversationSessionStarted", self._on_session_started)
        self.event_bus.subscribe("ConversationSessionEnded", self._on_session_ended)
        self.event_bus.subscribe("ConversationTurnStarted", self._on_turn_started)
        self.event_bus.subscribe("ConversationTurnCompleted", self._on_turn_completed)
        self.event_bus.subscribe("INTENT_GENERATED", self._on_intent)
        self.event_bus.subscribe("CapabilityExecuted", self._on_capability)
        
    def _on_send(self):
        text = self.text_input.text().strip()
        if text:
            self.text_input.clear()
            # Push to the semantic pipeline as if it were a transcript
            self.event_bus.publish(Event("USER_TRANSCRIPT_GENERATED", "ChatWorkspace", {"text": text, "session_id": "manual"}))

    @Slot(str)
    def _append_text(self, text: str):
        self.chat_display.append(text)
        
    def _on_session_started(self, event_data: Any):
        payload = getattr(event_data, "payload", {})
        if isinstance(event_data, dict): payload = event_data.get("payload", {})
        ev = payload.get("event")
        if ev:
            self.append_text_signal.emit(f"<b>--- Session Started ({ev.conversation_id}) ---</b><br>")
            
    def _on_session_ended(self, event_data: Any):
        payload = getattr(event_data, "payload", {})
        if isinstance(event_data, dict): payload = event_data.get("payload", {})
        ev = payload.get("event")
        if ev:
            self.append_text_signal.emit(f"<b>--- Session Ended ({ev.reason}) ---</b><br>")

    def _on_turn_started(self, event_data: Any):
        payload = getattr(event_data, "payload", {})
        if isinstance(event_data, dict): payload = event_data.get("payload", {})
        ev = payload.get("event")
        if ev:
            self.append_text_signal.emit(f"<span style='color:blue;'>👤 <b>You:</b> {ev.user_input}</span>")

    def _on_intent(self, event_data: Any):
        payload = getattr(event_data, "payload", {})
        if isinstance(event_data, dict): payload = event_data.get("payload", {})
        ev = payload.get("event")
        if ev and getattr(ev, "desktop_intent", None):
            action = ev.desktop_intent.action.name
            target = ev.desktop_intent.target
            self.append_text_signal.emit(f"<span style='color:purple;'>🧠 <b>Intent:</b> {action} {target}</span>")

    def _on_capability(self, event_data: Any):
        payload = getattr(event_data, "payload", {})
        if isinstance(event_data, dict): payload = event_data.get("payload", {})
        tool = payload.get("tool", "unknown")
        status = payload.get("status", "unknown")
        self.append_text_signal.emit(f"<span style='color:orange;'>⚙ <b>Execution:</b> {tool} [{status}]</span>")

    def _on_turn_completed(self, event_data: Any):
        payload = getattr(event_data, "payload", {})
        if isinstance(event_data, dict): payload = event_data.get("payload", {})
        ev = payload.get("event")
        if ev:
            self.append_text_signal.emit(f"<span style='color:green;'>🤖 <b>Chitti:</b> <i>{ev.response_text}</i></span><br>")
