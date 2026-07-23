import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from desktop.platform.shared.models.audio_state import AudioState
from desktop.platform.shared.models.knowledge import KnowledgeSnapshot


@dataclass
class LatencyMetrics:
    wake_detection_ms: float = 0.0
    stt_ms: float = 0.0
    llm_ms: float = 0.0
    planner_ms: float = 0.0
    tool_ms: float = 0.0
    tts_ms: float = 0.0
    playback_ms: float = 0.0

    @property
    def total_ms(self) -> float:
        return (
            self.wake_detection_ms
            + self.stt_ms
            + self.llm_ms
            + self.planner_ms
            + self.tool_ms
            + self.tts_ms
            + self.playback_ms
        )


@dataclass
class ConversationSession:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger: str = "Unknown"  # e.g., Voice, Desktop, Robot, Schedule
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    state: AudioState = AudioState.INITIALIZING
    wake_word: Optional[str] = None
    input_audio_path: Optional[str] = None
    recognized_text: Optional[str] = None
    intent: Optional[dict] = None
    workflow: Optional[dict] = None
    response_text: Optional[str] = None
    latency: LatencyMetrics = field(default_factory=LatencyMetrics)
    interruptions: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    context_snapshot: Optional[dict] = None
    health: str = "GOOD"
    knowledge_snapshot: Optional[KnowledgeSnapshot] = None
    
    # AI Trace Fields
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    finish_reason: Optional[str] = None
