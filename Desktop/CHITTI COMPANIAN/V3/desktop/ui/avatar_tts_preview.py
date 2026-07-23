import sys
import os
import traceback
import logging

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, v3_root)

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit
from PySide6.QtCore import QTimer

from desktop.platform.integrations.core.event_bus import EventBus
from desktop.ui.presence.presence_engine import PresenceEngine
from desktop.runtimes.expression.runtime import ExpressionRuntime
from desktop.runtimes.expression.outputs.voice.runtime import VoiceRuntime
from desktop.runtimes.expression.outputs.voice.events import SpeakRequested
from desktop.services.audio.providers.piper_provider import PiperProvider
from desktop.platform.integrations.core.provider_registry import SpeechSynthRegistry
from desktop.services.audio.speech_synth_router import SpeechSynthRouter

from desktop.ui.widget.companion_widget import CompanionWidget
from desktop.ui.widget.expression_controller import ExpressionController

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AvatarTTSPreview")

class MockLogger:
    def info(self, msg): logger.info(msg)
    def error(self, msg): logger.error(msg)
    def warning(self, msg): logger.warning(msg)
    def debug(self, msg): logger.debug(msg)
    def event(self, event_id, **kwargs): logger.info(f"EVENT: {event_id} {kwargs}")
    def exception(self, e, **kwargs): logger.error(f"EXCEPTION: {e} {kwargs}")

class AvatarTTSDevTool(QWidget):
    def __init__(self, widget: CompanionWidget, event_bus: EventBus):
        super().__init__()
        self.widget = widget
        self.event_bus = event_bus
        self.setWindowTitle("Avatar TTS Preview")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type what CHITTI should say...")
        layout.addWidget(self.input_field)
        
        self.speak_btn = QPushButton("Speak")
        self.speak_btn.clicked.connect(self.on_speak_clicked)
        layout.addWidget(self.speak_btn)
        
        self.interrupt_btn = QPushButton("Interrupt (Force Ready)")
        self.interrupt_btn.clicked.connect(self.on_interrupt_clicked)
        layout.addWidget(self.interrupt_btn)
        
        # Connect bridge
        self.controller = ExpressionController(event_bus)
        self.controller.animation_started_signal.connect(self.widget.handle_expression_started)
        
        try:
            self.widget.slide_in()
        except Exception as e:
            print("Failed to slide in:", e)

    def on_speak_clicked(self):
        text = self.input_field.text().strip()
        if text:
            # Emitting SpeakRequested will trigger:
            # 1. VoiceRuntime to start TTS & Playback
            # 2. PresenceEngine to switch to TALKING
            # 3. ExpressionRuntime to queue 'Talking' animation
            self.event_bus.publish(SpeakRequested(text=text))
            self.input_field.clear()

    def on_interrupt_clicked(self):
        # A Wake word simulates an interruption, which forces LISTENING
        from desktop.platform.shared.interfaces.event_bus import Event
        self.event_bus.publish(Event("WakeDetected", "Mic", {}))

def main():
    print("=== CHITTI AVATAR TTS INTEGRATION ===")
    
    app = QApplication(sys.argv)
    
    # 1. Backend Infrastructure
    mlogger = MockLogger()
    event_bus = EventBus(logger=mlogger)
    event_bus.start()
    
    # Piper TTS
    piper = PiperProvider(event_bus=event_bus, logger=mlogger)
    model_path = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\desktop\models\piper\en_US-amy-medium.onnx"
    if os.path.exists(model_path):
        piper.load_model(model_path)
    else:
        print(f"\n[ERROR] Piper model not found at {model_path}. Audio will fail. Run download script.")
        
    registry = SpeechSynthRegistry(logger=mlogger)
    registry.register_provider(piper)
    router = SpeechSynthRouter(registry=registry, logger=mlogger)
    
    # Runtimes
    voice_runtime = VoiceRuntime(event_bus=event_bus, speech_router=router)
    voice_runtime.start()
    
    presence_engine = PresenceEngine(event_bus)
    presence_engine.start()
    
    expr_runtime = ExpressionRuntime(event_bus)
    expr_runtime.start()
    
    # 2. UI Rendering
    try:
        companion = CompanionWidget()
        companion.show()
    except Exception as e:
        print("Failed to instantiate CompanionWidget:")
        traceback.print_exc()
        sys.exit(1)
        
    # 3. Developer Control Tool
    dev_tool = AvatarTTSDevTool(companion, event_bus)
    dev_tool.show()
    
    # The application loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
