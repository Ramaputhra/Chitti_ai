from desktop.platform.shared.interfaces.event_bus import Event

class SpeakRequested(Event):
    """Fired when a component (like Planner/Capabilities) requests TTS."""
    def __init__(self, text: str, voice: str = "default", interruptible: bool = True):
        super().__init__(
            event_id="Voice.SpeakRequested",
            source="ExpressionPipeline",
            payload={"text": text, "voice": voice, "interruptible": interruptible}
        )
        self.text = text
        self.voice = voice
        self.interruptible = interruptible

class SynthesisStarted(Event):
    """Fired when TTS inference actually begins."""
    def __init__(self, text: str):
        super().__init__("Voice.SynthesisStarted", "VoiceRuntime", {"text": text})

class AudioStarted(Event):
    """Fired when the first PCM buffer hits the speaker output."""
    def __init__(self):
        super().__init__("Voice.AudioStarted", "VoiceRuntime", {})

class AudioFinished(Event):
    """Fired when the audio buffer completes playback fully."""
    def __init__(self):
        super().__init__("Voice.AudioFinished", "VoiceRuntime", {})

class SpeakCompleted(Event):
    """Fired when the entire SpeakRequested lifecycle is successfully done."""
    def __init__(self):
        super().__init__("Voice.SpeakCompleted", "VoiceRuntime", {})

class SpeakInterrupted(Event):
    """Fired when a voice stream is cancelled prematurely (Rule 44)."""
    def __init__(self, reason: str = "new_focus"):
        super().__init__("Voice.SpeakInterrupted", "VoiceRuntime", {"reason": reason})
