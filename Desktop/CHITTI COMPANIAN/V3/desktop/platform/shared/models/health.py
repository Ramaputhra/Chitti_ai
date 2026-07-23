from dataclasses import dataclass
from typing import Optional

@dataclass
class ProviderHealth:
    """
    Standardized health object for all providers per P0-001.
    """
    status: str
    healthy: bool
    enabled: bool
    configured: bool
    authenticated: bool
    latency_ms: int
    last_error: Optional[str]
    version: str
    model: str
    uptime: int
