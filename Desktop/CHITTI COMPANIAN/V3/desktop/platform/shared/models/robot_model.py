from dataclasses import dataclass, field
from typing import Dict

from desktop.platform.shared.models.perception_model import PerceptionModel


@dataclass
class TouchState:
    zone: str = ""  # e.g., "Head", "Left Ear", "Right Ear"
    action: str = ""  # e.g., "Petting", "Tap", "Long Press"
    intensity: float = 0.0


@dataclass
class MotionState:
    status: str = "Stationary"  # e.g., "Moving", "Fallen", "Lifted"
    orientation: Dict[str, float] = field(default_factory=dict)
    acceleration: Dict[str, float] = field(default_factory=dict)


@dataclass
class PowerState:
    voltage: float = 0.0
    current: float = 0.0
    charging: bool = False
    temperature: float = 0.0
    health: str = "Good"
    estimated_runtime_minutes: int = 0


@dataclass
class EnvironmentState:
    obstacle_detected: bool = False
    direction: str = ""
    distance_cm: float = 0.0
    status: str = "Clear"  # e.g., "Approaching", "Leaving"


@dataclass
class ConnectivityState:
    usb_connected: bool = False
    wifi_connected: bool = False
    bt_connected: bool = False
    latency_ms: float = 0.0
    packet_loss_percent: float = 0.0


@dataclass
class HealthState:
    cpu_temperature: float = 0.0
    memory_usage_percent: float = 0.0
    sensor_status: str = "Nominal"
    servo_status: str = "Nominal"


@dataclass
class RobotModel(PerceptionModel):
    """
    The unified domain model built by the Robot Analyzer before any artifacts 
    or attention events are generated. Fulfills Engineering Rule #14 for hardware embodiment.
    """
    touch: TouchState = field(default_factory=TouchState)
    motion: MotionState = field(default_factory=MotionState)
    power: PowerState = field(default_factory=PowerState)
    environment: EnvironmentState = field(default_factory=EnvironmentState)
    connectivity: ConnectivityState = field(default_factory=ConnectivityState)
    health: HealthState = field(default_factory=HealthState)
