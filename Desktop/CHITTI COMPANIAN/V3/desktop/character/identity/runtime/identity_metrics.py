from dataclasses import dataclass

@dataclass
class IdentityMetrics:
    """
    S36C: Telemetry metrics for Identity Platform.
    """
    profile_load_count: int = 0
    hot_reload_count: int = 0
    context_build_count: int = 0
    canonical_queries_count: int = 0
    validation_failures: int = 0
