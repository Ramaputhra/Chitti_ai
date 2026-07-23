from dataclasses import dataclass
from typing import Optional

@dataclass
class Span:
    name: str
    parent_name: Optional[str] = None
    duration_ms: float = 0.0
    status: str = "OK"

class ExecutionTracer:
    def __init__(self):
        self._completed_spans = []

    def record_span(self, span: Span):
        self._completed_spans.append(span)
        if len(self._completed_spans) > 500:
            self._completed_spans.pop(0)

    def get_traces(self):
        return self._completed_spans
