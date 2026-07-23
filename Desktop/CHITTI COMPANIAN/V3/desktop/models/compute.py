from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SchedulingDecision(Enum):
    KEEP_LOCAL = 1
    SWAP_MODEL = 2
    MOVE_TO_CLOUD = 3
    QUEUE = 4
    PREEMPT = 5

class ResidencyPolicy(Enum):
    PINNED = 1
    WARM = 2
    STANDBY = 3
    UNLOAD_IMMEDIATELY = 4

@dataclass
class InferenceRequirement:
    """The capability-based request replacing model names (Rule 163)."""
    reasoning_level: str # Low, Medium, High
    vision_required: bool
    embedding_required: bool
    speech_required: bool
    latency_priority: str # Critical, High, Low
    privacy_priority: str # LocalRequired, CloudAllowed
    quality_priority: str
    streaming: bool
    tool_calling: bool

@dataclass
class ComputePolicy:
    """User or system defined operational boundaries."""
    prefer_local: bool
    allow_cloud: bool
    max_latency_ms: int
    max_memory_gb: int
    privacy_level: str
    battery_policy: str # AggressivePowerSave, Balanced, MaxPerformance
    max_cost_per_request: float # Cost awareness

@dataclass
class ComputeResources:
    """Hardware state replacing HardwareConstraints."""
    cpu_utilization: float
    gpu_utilization: float
    npu_utilization: float
    ram_available_gb: float
    vram_available_gb: float
    disk_bandwidth_mb: float
    thermal_throttling: bool
    battery_percentage: float
    network_latency_ms: int

@dataclass
class ModelProfile:
    id: str
    family: str
    provider: str
    capabilities: List[str]
    modalities: List[str]
    context_window: int
    quantization: str
    memory_requirements_gb: float
    latency_profile: str
    throughput_profile: str
    quality_profile: str
    supported_tasks: List[str]
    local_only: bool
    cloud_only: bool
    estimated_cost: float # Cloud API cost or Energy cost

@dataclass
class ModelHealth:
    loaded: bool
    warm: bool
    idle: bool
    memory_used_gb: float
    errors: int
    last_used: datetime
    average_latency_ms: float

@dataclass
class ComputeAllocation:
    """The outcome of the scheduler."""
    task: str
    requested_capabilities: InferenceRequirement
    selected_model_id: str
    selected_provider: str
    priority: int
    reason: str
    expected_duration_ms: int
    residency: ResidencyPolicy
