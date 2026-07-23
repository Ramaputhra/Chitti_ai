"""
Health Check Service

Provides centralized health monitoring for all CHITTI runtimes.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import time

from desktop.models.lifecycle import IRuntime, HealthState


class ComponentStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status of a single component."""
    name: str
    status: ComponentStatus
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    last_check: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    response_time_ms: Optional[float] = None


@dataclass
class SystemHealth:
    """Aggregated system health status."""
    overall_status: ComponentStatus
    version: str = "1.0.0"
    uptime_seconds: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    components: List[ComponentHealth] = field(default_factory=list)
    
    @property
    def healthy_count(self) -> int:
        return sum(1 for c in self.components if c.status == ComponentStatus.HEALTHY)
    
    @property
    def unhealthy_count(self) -> int:
        return sum(1 for c in self.components if c.status == ComponentStatus.UNHEALTHY)
    
    @property
    def degraded_count(self) -> int:
        return sum(1 for c in self.components if c.status == ComponentStatus.DEGRADED)


class HealthCheckService:
    """
    Service for performing health checks on all system components.
    """
    
    def __init__(self, version: str = "1.0.0"):
        self.version = version
        self._start_time = time.time()
        self._runtimes: Dict[str, IRuntime] = {}
        self._custom_checks: Dict[str, callable] = {}
    
    def register_runtime(self, name: str, runtime: IRuntime) -> None:
        """Register a runtime for health monitoring."""
        self._runtimes[name] = runtime
    
    def register_check(self, name: str, check_fn: callable) -> None:
        """Register a custom health check function."""
        self._custom_checks[name] = check_fn
    
    async def check_runtime(self, name: str, runtime: IRuntime) -> ComponentHealth:
        """Perform health check on a single runtime."""
        start = time.time()
        try:
            health_state = runtime.health()
            
            # Map HealthState to ComponentStatus
            if health_state == HealthState.HEALTHY:
                status = ComponentStatus.HEALTHY
            elif health_state == HealthState.DEGRADED:
                status = ComponentStatus.DEGRADED
            else:
                status = ComponentStatus.UNHEALTHY
            
            response_time = (time.time() - start) * 1000
            
            return ComponentHealth(
                name=name,
                status=status,
                response_time_ms=response_time,
                last_check=datetime.now(timezone.utc)
            )
        except Exception as e:
            return ComponentHealth(
                name=name,
                status=ComponentStatus.UNHEALTHY,
                message=str(e),
                response_time_ms=(time.time() - start) * 1000,
                last_check=datetime.now(timezone.utc)
            )
    
    async def check_custom(self, name: str, check_fn: callable) -> ComponentHealth:
        """Perform a custom health check."""
        start = time.time()
        try:
            if asyncio.iscoroutinefunction(check_fn):
                result = await check_fn()
            else:
                result = check_fn()
            
            response_time = (time.time() - start) * 1000
            
            if result is True:
                status = ComponentStatus.HEALTHY
            elif result is False:
                status = ComponentStatus.UNHEALTHY
            elif isinstance(result, dict):
                status = ComponentStatus(result.get("status", "unknown"))
            else:
                status = ComponentStatus.HEALTHY
            
            return ComponentHealth(
                name=name,
                status=status,
                response_time_ms=response_time,
                last_check=datetime.now(timezone.utc)
            )
        except Exception as e:
            return ComponentHealth(
                name=name,
                status=ComponentStatus.UNHEALTHY,
                message=str(e),
                response_time_ms=(time.time() - start) * 1000,
                last_check=datetime.now(timezone.utc)
            )
    
    async def get_system_health(self) -> SystemHealth:
        """Get aggregated health status of the entire system."""
        components = []
        
        # Check all runtimes
        for name, runtime in self._runtimes.items():
            component = await self.check_runtime(name, runtime)
            components.append(component)
        
        # Run custom checks
        for name, check_fn in self._custom_checks.items():
            component = await self.check_custom(name, check_fn)
            components.append(component)
        
        # Determine overall status
        if any(c.status == ComponentStatus.UNHEALTHY for c in components):
            overall = ComponentStatus.UNHEALTHY
        elif any(c.status == ComponentStatus.DEGRADED for c in components):
            overall = ComponentStatus.DEGRADED
        else:
            overall = ComponentStatus.HEALTHY
        
        return SystemHealth(
            overall_status=overall,
            version=self.version,
            uptime_seconds=time.time() - self._start_time,
            components=components
        )
    
    async def is_healthy(self) -> bool:
        """Quick check if system is healthy."""
        health = await self.get_system_health()
        return health.overall_status == ComponentStatus.HEALTHY
    
    def get_health_report(self) -> Dict[str, Any]:
        """Generate a health report suitable for JSON serialization."""
        # Synchronous version for quick checks
        components = []
        for name, runtime in self._runtimes.items():
            try:
                health_state = runtime.health()
                if health_state == HealthState.HEALTHY:
                    status = "healthy"
                elif health_state == HealthState.DEGRADED:
                    status = "degraded"
                else:
                    status = "unhealthy"
                components.append({"name": name, "status": status})
            except Exception:
                components.append({"name": name, "status": "unknown"})
        
        # Determine overall status
        if any(c["status"] == "unhealthy" for c in components):
            overall = "unhealthy"
        elif any(c["status"] == "degraded" for c in components):
            overall = "degraded"
        else:
            overall = "healthy"
        
        return {
            "status": overall,
            "version": self.version,
            "uptime_seconds": time.time() - self._start_time,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": components
        }


# Import asyncio for async checks
import asyncio


# Global health service instance
_health_service: Optional[HealthCheckService] = None


def get_health_service() -> HealthCheckService:
    """Get the global health service instance."""
    global _health_service
    if _health_service is None:
        _health_service = HealthCheckService()
    return _health_service
