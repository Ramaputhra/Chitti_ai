from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List

@dataclass
class TraceNode:
    stage: str
    start_time: datetime
    end_time: datetime
    latency_ms: float
    input_size_bytes: int
    output_summary: str
    evidence: Dict[str, Any]
    telemetry: Dict[str, Any]

@dataclass
class CognitiveTrace:
    """
    A complete reasoning trace of a single CHITTI request.
    Records Observe -> Understand -> Context -> Memory -> Prediction -> Planner -> Workflow -> Execution.
    """
    trace_id: str
    trigger: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = None
    nodes: List[TraceNode] = field(default_factory=list)
    total_latency_ms: float = 0.0

class CognitiveTraceLogger:
    def __init__(self):
        self.active_traces: Dict[str, CognitiveTrace] = {}
        
    def start_trace(self, trace_id: str, trigger: str):
        self.active_traces[trace_id] = CognitiveTrace(trace_id=trace_id, trigger=trigger)
        
    def add_node(self, trace_id: str, node: TraceNode):
        if trace_id in self.active_traces:
            self.active_traces[trace_id].nodes.append(node)
            
    def complete_trace(self, trace_id: str):
        if trace_id in self.active_traces:
            trace = self.active_traces[trace_id]
            trace.end_time = datetime.now()
            trace.total_latency_ms = sum(n.latency_ms for n in trace.nodes)
            return trace
        return None
