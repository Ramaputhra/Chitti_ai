from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time

class ConversationStateEnum(Enum):
    ACTIVE = "ACTIVE"
    PAUSED_BY_USER = "PAUSED_BY_USER"
    PAUSED_SYSTEM_TRAY = "PAUSED_SYSTEM_TRAY"
    PAUSED_FULLSCREEN = "PAUSED_FULLSCREEN"
    PAUSED_PRESENTATION = "PAUSED_PRESENTATION"
    INTERRUPTED = "INTERRUPTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class ConversationContext:
    conversation_id: str = "conv_default"
    current_intent: str = "GENERAL"
    current_capability: str = "general_assistant"
    speech_offset: float = 0.0
    narration_offset: int = 0
    last_spoken_sentence: str = ""
    remaining_queue: List[str] = field(default_factory=list)
    pause_timestamp: float = 0.0
    resume_allowed: bool = True
    stop_reason: str = "none"
    state: ConversationStateEnum = ConversationStateEnum.COMPLETED

    def pause_by_user(self, reason: str = "Middle click on Presence Dot"):
        self.state = ConversationStateEnum.PAUSED_BY_USER
        self.pause_timestamp = time.time()
        self.stop_reason = reason

    def pause_system_tray(self, reason: str = "System Tray mode"):
        self.state = ConversationStateEnum.PAUSED_SYSTEM_TRAY
        self.pause_timestamp = time.time()
        self.stop_reason = reason

    def resume(self) -> bool:
        if self.resume_allowed:
            self.state = ConversationStateEnum.ACTIVE
            return True
        return False
