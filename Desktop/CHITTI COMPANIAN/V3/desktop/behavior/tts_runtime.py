from abc import ABC, abstractmethod
from typing import AsyncIterable, Optional
from desktop.behavior.character_models import FinalDialogue
from desktop.behavior.tts_models import SpeechQueueItem, VisemeTimeline, VoiceProfile

class ITTSProvider(ABC):
    @abstractmethod
    async def synthesize_stream(self, text: str, profile: VoiceProfile) -> AsyncIterable[bytes]:
        """Streams audio chunks back to the mixer for low-latency playback."""
        pass
        
    @abstractmethod
    def generate_visemes(self, text: str, audio_envelope: Optional[bytes] = None) -> VisemeTimeline:
        """Generates viseme timelines, ideally natively, fallback to phoneme parsing or envelope estimation."""
        pass

class ISpeechQueue(ABC):
    @abstractmethod
    def enqueue(self, item: SpeechQueueItem): pass
    
    @abstractmethod
    def next(self) -> Optional[SpeechQueueItem]: pass
    
    @abstractmethod
    def evaluate_interrupt(self, incoming: SpeechQueueItem, active: SpeechQueueItem) -> bool:
        """Determines if incoming speech should preempt active speech based on InterruptPolicy."""
        pass

class IAudioCache(ABC):
    @abstractmethod
    def get_cached_audio(self, dialogue_id: str, profile_id: str) -> Optional[bytes]: pass
    
    @abstractmethod
    def cache_audio(self, dialogue_id: str, profile_id: str, audio_data: bytes): pass

class ISpeechMixer(ABC):
    @abstractmethod
    async def play_stream(self, stream: AsyncIterable[bytes], channel: str = "SPEECH"): pass
    
    @abstractmethod
    def stop(self, channel: str = "SPEECH"): pass
    
    @abstractmethod
    def set_ducking(self, background_volume_percent: float):
        """Lowers volume of MEDIA/UI channels while SPEECH channel is active."""
        pass

class ITTSRuntime(ABC):
    """
    Consumes FinalDialogue, orchestrates the SpeechQueue and Cache, streams via 
    ITTSProvider (e.g. ElevenLabs), mixes the audio with ducking, and emits VisemeTimelines.
    """
    @abstractmethod
    async def process_final_dialogue(self, dialogue: FinalDialogue): pass
    
    @abstractmethod
    def get_provider_chain(self) -> list[ITTSProvider]:
        """Returns the fallback chain of providers (e.g. Cloud -> Local)."""
        pass
