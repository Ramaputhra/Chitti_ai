import asyncio
from typing import Callable, Awaitable
from desktop.app.transports import ITransport
from desktop.models.events import SystemEvent, KernelShutdownRequest
from desktop.models.presentation import RenderedExpression, ExpressionDelivered
from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus

# Audio Services
from desktop.services.audio.device_manager import AudioDeviceManager
from desktop.services.audio.microphone_manager import MicrophoneManager
from desktop.services.audio.speaker_manager import SpeakerManager
from desktop.services.audio.vad.energy_vad import EnergyVAD
from desktop.services.audio.audio_pipeline import AudioPipeline
from desktop.services.audio.providers.open_wake_word_provider import OpenWakeWordProvider
from desktop.services.audio.providers.faster_whisper_provider import FasterWhisperProvider
from desktop.services.audio.providers.piper_provider import PiperProvider
from desktop.platform.integrations.core.logging_service import LoggingService


class VoiceTransport(ITransport):
    """
    Translates Voice interactions into Kernel InteractionEnvelopes.
    Wires the local Audio Pipeline, STT, and Wake Word.
    """
    def __init__(self):
        self.on_input: Callable[[str, str], Awaitable[None]] = None
        self._running = False
        self.event_bus: IEventBus = None
        self.logger = LoggingService("logs") # basic local logger
        self.logger.initialize()
        
        # We will instantiate the audio capabilities here
        class DummySettings:
            def get(self, key, default=None): return default
            def set(self, key, value): pass
            
        dummy_settings = DummySettings()
        self.device_manager = AudioDeviceManager(self.event_bus, self.logger, dummy_settings) if self.event_bus else None
        self.microphone = None
        self.speaker = None
        self.vad = None
        self.audio_pipeline = None
        self.wake_word = None
        self.stt = None
        self.tts = None
        
    def set_event_bus(self, event_bus: IEventBus):
        self.event_bus = event_bus
        
        class DummySettings:
            def get(self, key, default=None): return default
            def set(self, key, value): pass
            
        dummy_settings = DummySettings()
        
        self.device_manager = AudioDeviceManager(self.event_bus, self.logger, dummy_settings)
        self.microphone = MicrophoneManager(self.event_bus, self.logger, self.device_manager)
        self.speaker = SpeakerManager(self.event_bus, self.logger, self.device_manager)
        
        # We need to handle VAD instantiation
        self.vad = EnergyVAD()
        self.audio_pipeline = AudioPipeline(self.event_bus, self.logger, self.vad)
        
        self.wake_word = OpenWakeWordProvider(self.event_bus, self.logger)
        self.stt = FasterWhisperProvider(self.event_bus, self.logger)
        self.tts = PiperProvider(self.event_bus, self.logger)

        # Wire the event loop hooks
        # When wake word detects "hey chitti", it emits Voice.WakeDetected. We then emit Session.Started
        self.event_bus.subscribe("Voice.WakeDetected", self._on_wake_detected)
        
        # When AudioPipeline emits VOICE_AUDIO_READY, STT handles it automatically (WhisperProvider subscribes to it).
        # When STT finishes, it emits SystemEvents.LANGUAGE_TEXT_RECOGNIZED. We capture it to send to Kernel.
        self.event_bus.subscribe(SystemEvents.LANGUAGE_TEXT_RECOGNIZED, self._on_transcription_completed)

    async def start(self):
        self._running = True
        
        # Initialize Services
        self.device_manager.initialize()
        self.microphone.initialize()
        self.speaker.initialize()
        
        self.audio_pipeline.initialize()
        self.wake_word.initialize()
        self.stt.initialize()
        self.tts.initialize()

        # Start capturing mic audio (feeds to OpenWakeWord and AudioPipeline)
        self.microphone.start_capture()
        self.wake_word.start_listening()
        
        print("    [VoiceTransport] Started. Listening for Wake Word ('hey_jarvis' or default).")

    async def stop(self):
        self._running = False
        self.microphone.shutdown()
        self.wake_word.shutdown()
        self.audio_pipeline.shutdown()
        self.stt.shutdown()
        self.tts.shutdown()
        print("    [VoiceTransport] Stopped.")

    def _on_wake_detected(self, event: Event):
        print(f"\n[VoiceTransport] 🗣️ Wake Word Detected: {event.payload.get('wake_word')}")
        # Transition from Wake Word -> Pipeline buffering
        self.event_bus.publish(Event("Session.Started", "VoiceTransport", {}))
        
    def _on_transcription_completed(self, event: Event):
        text = event.payload.get("text")
        if text and self.on_input:
            print(f"[VoiceTransport] User said: {text}")
            # Ensure it doesn't block the event bus thread; inject into the asyncio loop
            if hasattr(self, 'kernel') and self.kernel and self.kernel.context.loop:
                asyncio.run_coroutine_threadsafe(self.on_input(text, "Voice"), self.kernel.context.loop)
            else:
                print("[VoiceTransport] ERROR: Cannot inject input, no kernel loop available.")
            # Re-enable wake word listening for the next round
            self.wake_word.start_listening()

    async def deliver(self, expr: RenderedExpression, event_bus):
        if "audio" in expr.formats or "text" in expr.formats:
            text = expr.formats.get('text', '')
            print(f"[VoiceTransport] Emitting TTS for: {text}")
            
            # Request TTS to speak
            event_bus.publish(Event(SystemEvents.VOICE_TTS_REQUEST, "VoiceTransport", {"text": text, "correlation_id": expr.correlation_id}))
            
            # Since TTS/Speaker is asynchronous, we might want to confirm delivery immediately or wait.
            # Simplified confirmation:
            from datetime import datetime
            event_bus.publish(ExpressionDelivered(
                timestamp=datetime.now(),
                source="VoiceTransport",
                correlation_id=expr.correlation_id,
                domain="Presentation",
                action="ExpressionDelivered",
                interaction_id=expr.interaction_id,
                session_id="default_session",
                delivered_format="audio",
                content=text
            ))
