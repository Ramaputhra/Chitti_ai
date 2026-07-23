from enum import Enum
from dataclasses import dataclass

class CapabilityProfile(Enum):
    LOCAL_FULL = "LOCAL_FULL"
    LOCAL_LIMITED = "LOCAL_LIMITED"
    HYBRID = "HYBRID"
    CLOUD_REQUIRED = "CLOUD_REQUIRED"

@dataclass
class HardwareProfile:
    ram_gb: float
    vram_gb: float
    gpu_name: str
    cpu_name: str
    supports_cuda: bool
    supports_directml: bool
    supports_onnx: bool
    profile: CapabilityProfile
