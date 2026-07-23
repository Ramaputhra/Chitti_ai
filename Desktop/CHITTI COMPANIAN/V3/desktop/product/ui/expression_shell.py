import os
import numpy as np
from PySide6.QtCore import Qt, QPoint, Signal, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QPushButton, QApplication, QLineEdit

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.event_bus import IEventBus, Event
from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.models.audio import AudioPacket
from .components.avatar_renderer import AvatarRenderer

from desktop.runtimes.presence.activity_monitor import ActivityMonitor
from desktop.runtimes.presence.monitor import MonitorManager

class ExpressionShell(QWidget):
    audio_level_signal = Signal(int)

    def __init__(self, logger: ILoggingService, event_bus: IEventBus, activity_monitor: ActivityMonitor, monitor_manager: MonitorManager):
        super().__init__()
        self.logger = logger
        self.event_bus = event_bus
        self.activity_monitor = activity_monitor
        self.monitor_manager = monitor_manager
        
        # UI Setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(320, 300)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.main_layout)

        self.layout = QHBoxLayout()
        self.main_layout.addLayout(self.layout)
        
        # Left side: close button + Avatar
        self.left_container = QWidget()
        self.left_layout = QVBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 60, 60, 200);
                color: white;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 255);
            }
        """)
        self.close_btn.clicked.connect(self._on_close_clicked)
        self.left_layout.addWidget(self.close_btn, alignment=Qt.AlignRight)
        
        # Avatar Renderer (Replaces the static Emoji Label)
        self.avatar = AvatarRenderer(self.logger, self.left_container)
        self.avatar.setFixedSize(200, 200)
        
        # Load the classic profile
        profile_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "avatar", "classic", "profile.yaml"))
        self.avatar.load_profile(profile_path)
        
        self.left_layout.addWidget(self.avatar, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.left_container)
        
        # Right side: Audio Visualizer (Speech Halo proxy)
        self.audio_bar = QProgressBar()
        self.audio_bar.setOrientation(Qt.Vertical)
        self.audio_bar.setRange(0, 100)
        self.audio_bar.setValue(0)
        self.audio_bar.setFixedWidth(15)
        self.audio_bar.setTextVisible(False)
        self.audio_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(30, 30, 30, 150);
                border-radius: 7px;
            }
            QProgressBar::chunk {
                background-color: #50e3c2;
                border-radius: 7px;
            }
        """)
        self.layout.addWidget(self.audio_bar)
        
        # Bottom: Developer Text Input
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Bypass mic: Type command here...")
        self.text_input.setStyleSheet("background: #2a2a2a; color: white; padding: 5px; border-radius: 5px;")
        self.text_input.returnPressed.connect(self._on_text_entered)
        self.main_layout.addWidget(self.text_input)
        
        # Dragging state
        self._drag_pos = QPoint()
        self._is_dragged = False
        
        # Connect Signals
        self.audio_level_signal.connect(self._set_audio_level_slot)

        self._subscribe_events()

    def _on_close_clicked(self) -> None:
        self.logger.info("User clicked close button on ExpressionShell.")
        QApplication.instance().quit()

    def _on_text_entered(self) -> None:
        text = self.text_input.text().strip()
        if text:
            self.logger.info(f"Dev input entered: {text}")
            self.event_bus.publish(
                Event("Voice.WakeDetected", "ExpressionShell", {})
            )
            self.event_bus.publish(
                Event("Session.Started", "ExpressionShell", {})
            )
            # Small delay to let Session start, then send transcript directly to language runtime
            from PySide6.QtCore import QTimer
            QTimer.singleShot(100, lambda: self._inject_transcript(text))
            
    def _inject_transcript(self, text: str) -> None:
        self.event_bus.publish(
            Event(
                SystemEvents.LANGUAGE_TEXT_RECOGNIZED,
                "ExpressionShell",
                {"text": text, "source": "developer_console"}
            )
        )
        self.text_input.clear()

    def _subscribe_events(self) -> None:
        # 1. Map new Expression states to the Avatar
        self.event_bus.subscribe("Expression.StateChanged", self._on_expression_state_changed)
        
        # 2. Map audio frames to the visualizer only
        self.event_bus.subscribe(SystemEvents.VOICE_AUDIO_FRAME, self._on_audio_frame)
        
    @Slot(int)
    def _set_audio_level_slot(self, level: int) -> None:
        self.audio_bar.setValue(level)

    def _on_expression_state_changed(self, event: Event) -> None:
        """
        The only driver for semantic visual states.
        No longer infers emotion from raw audio/intent events.
        """
        activity = event.payload.get("activity", "idle")
        
        # Safely marshal to UI thread
        from PySide6.QtCore import QMetaObject, Qt, Q_ARG
        QMetaObject.invokeMethod(self.avatar, "request_state", Qt.QueuedConnection, Q_ARG(str, activity))

    def _on_audio_frame(self, event: Event) -> None:
        """
        Drives the Speech Halo / Visualizer using raw amplitude.
        Does not change semantic expression.
        """
        packet: AudioPacket = event.payload.get("packet")
        if not packet:
            return
            
        try:
            audio_data = np.frombuffer(packet.data, dtype=np.int16)
            if len(audio_data) == 0:
                return
                
            float_data = audio_data.astype(np.float32) / 32768.0
            rms = np.sqrt(np.mean(np.square(float_data)))
            
            level = min(int(rms * 1000), 100)
            self.audio_level_signal.emit(level)
        except Exception:
            pass

    # --- Mouse & Monitor Tracking ---
    def enterEvent(self, event):
        self.activity_monitor.report_mouse_activity(is_hovering=True, is_dragged=self._is_dragged, is_click=False)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.activity_monitor.report_mouse_activity(is_hovering=False, is_dragged=self._is_dragged, is_click=False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            self._is_dragged = True
            self.monitor_manager.update_last_active_from_mouse(event.globalPos())
            self.activity_monitor.report_mouse_activity(is_hovering=True, is_dragged=self._is_dragged, is_click=True)
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            self.monitor_manager.update_last_active_from_mouse(event.globalPos())
            event.accept()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragged = False
            self.activity_monitor.report_mouse_activity(is_hovering=True, is_dragged=self._is_dragged, is_click=False)
            event.accept()
