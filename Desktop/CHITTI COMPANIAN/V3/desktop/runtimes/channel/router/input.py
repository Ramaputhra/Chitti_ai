from typing import Dict, Any
from desktop.runtimes.channel.models.core import ChannelType

class ChannelRouter:
    """
    Normalizes all incoming input (Voice, Desktop UI, Mobile Chat).
    Routes them agnostically into the Conversation Runtime.
    """
    
    def __init__(self):
        # In physical implementation, holds ref to ConversationRuntime
        pass
        
    def route_input(self, channel: ChannelType, payload: str, metadata: Dict[str, Any] = None):
        """
        Takes raw input from any channel and normalizes it.
        This completely decouples WakeWord/STT from the core AI loop.
        """
        print(f"[ChannelRouter] Received input from {channel.value}: {payload}")
        
        normalized_intent = {
            "source_channel": channel.value,
            "raw_text": payload,
            "metadata": metadata or {}
        }
        
        # Passes to Conversation Runtime
        self._dispatch_to_conversation_runtime(normalized_intent)
        
    def _dispatch_to_conversation_runtime(self, intent: Dict[str, Any]):
        print(f"[ChannelRouter] Dispatching to ConversationRuntime: {intent['raw_text']}")
