import heapq
from dataclasses import dataclass, field
from typing import List, Optional
from desktop.voice.runtime.speech_session import SpeechSession

@dataclass(order=True)
class PrioritizedSpeechSession:
    priority_score: int
    created_at: float
    session: SpeechSession = field(compare=False)

class SpeechQueue:
    """
    S36A: Priority speech queue supporting interrupt, replace, append, merge, and cancel operations.
    """
    PRIORITY_MAP = {
        "INTERRUPT": -10,
        "HIGH": -5,
        "NORMAL": 0,
        "LOW": 5
    }

    def __init__(self):
        self._heap: List[PrioritizedSpeechSession] = []

    def append(self, session: SpeechSession, priority: str = "NORMAL"):
        score = self.PRIORITY_MAP.get(priority.upper(), 0)
        heapq.heappush(self._heap, PrioritizedSpeechSession(priority_score=score, created_at=session.created_at, session=session))

    def pop(self) -> Optional[SpeechSession]:
        if self._heap:
            return heapq.heappop(self._heap).session
        return None

    def peek(self) -> Optional[SpeechSession]:
        if self._heap:
            return self._heap[0].session
        return None

    def replace(self, session: SpeechSession):
        self.clear()
        self.append(session, priority="INTERRUPT")

    def interrupt(self, session: SpeechSession):
        self.append(session, priority="INTERRUPT")

    def clear(self):
        self._heap.clear()

    @property
    def is_empty(self) -> bool:
        return len(self._heap) == 0

    @property
    def size(self) -> int:
        return len(self._heap)
