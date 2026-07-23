import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timezone

from desktop.core.runtime import IRuntime, RuntimeState, RestartPolicy
from desktop.models.events import SystemEvent

# --- Supervisor Events ---

@dataclass
class RuntimeStateChanged(SystemEvent):
    event_type: str = "RuntimeStateChanged"
    runtime_name: str = ""
    old_state_name: str = ""
    new_state_name: str = ""
    reason: str = ""

@dataclass
class RuntimeFaultDetected(SystemEvent):
    event_type: str = "RuntimeFaultDetected"
    runtime_name: str = ""
    error_message: str = ""
    traceback_info: str = ""

@dataclass
class RuntimeRestartAttempted(SystemEvent):
    event_type: str = "RuntimeRestartAttempted"
    runtime_name: str = ""
    attempt_number: int = 0
    max_retries: int = 0

# --- Supervisor Interface ---

class IRuntimeSupervisor(ABC):
    @abstractmethod
    def get_runtime_id(self) -> str:
        pass

    @abstractmethod
    def get_supervised_runtime(self) -> IRuntime:
        pass

    @abstractmethod
    async def start_supervision(self) -> None:
        pass

    @abstractmethod
    async def stop_supervision(self) -> None:
        pass

    @abstractmethod
    async def restart_runtime(self) -> None:
        pass

# --- Health Monitoring & Supervision ---

class BaseRuntimeSupervisor(IRuntimeSupervisor):
    def __init__(self, runtime: IRuntime, event_publisher: Callable[[SystemEvent], None]):
        self._runtime = runtime
        self._metadata = runtime.get_metadata()
        self._name = self._metadata.runtime_id
        self._publish = event_publisher
        
        self._monitor_task: Optional[asyncio.Task] = None
        self._is_supervising = False
        self._restart_attempts = 0

    def get_runtime_id(self) -> str:
        return self._name

    def get_supervised_runtime(self) -> IRuntime:
        return self._runtime

    async def start_supervision(self) -> None:
        if self._is_supervising:
            return
        
        self._is_supervising = True
        
        try:
            await self._runtime.initialize()
            await self._runtime.start()
            self._publish(RuntimeStateChanged(self._name, RuntimeState.CREATED.name, RuntimeState.RUNNING.name, "Started"))
            
            self._monitor_task = asyncio.create_task(self._monitor_loop())
        except Exception as e:
            self._publish(RuntimeFaultDetected(self._name, f"Initialization failed: {e}", ""))
            self._is_supervising = False
            self._publish(RuntimeStateChanged(self._name, RuntimeState.CREATED.name, RuntimeState.FAILED.name, "Init failed"))
            raise

    async def stop_supervision(self) -> None:
        self._is_supervising = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        try:
            await self._runtime.stop()
        except Exception as e:
            self._publish(RuntimeFaultDetected(self._name, f"Stop failed: {e}", ""))
            
        self._publish(RuntimeStateChanged(self._name, RuntimeState.RUNNING.name, RuntimeState.STOPPED.name, "Stopped"))

    async def restart_runtime(self) -> None:
        health_policy = self._metadata.health_policy
        self._publish(RuntimeRestartAttempted(self._name, self._restart_attempts, health_policy.max_retries))
        
        restart_policy = self._metadata.restart_policy
        if restart_policy == RestartPolicy.NEVER:
            self._publish(RuntimeFaultDetected(self._name, "Restart not supported by RestartPolicy.NEVER.", ""))
            raise RuntimeError(f"Runtime {self._name} does not support restarting.")
            
        try:
            await self._runtime.stop()
        except Exception:
            pass
            
        await self._runtime.initialize()
        await self._runtime.start()
        self._publish(RuntimeStateChanged(self._name, RuntimeState.RESTARTING.name, RuntimeState.RUNNING.name, "Restarted successfully"))

    async def _monitor_loop(self) -> None:
        health_policy = self._metadata.health_policy
        
        while self._is_supervising:
            try:
                # Active Health Check
                health = await asyncio.wait_for(
                    self._runtime.health_check(), 
                    timeout=health_policy.interval_seconds
                )
                
                if not health.healthy:
                    raise Exception(f"Runtime reported unhealthy: {health.details}")
                    
                # Timeout Detection
                if health.last_heartbeat:
                    now = datetime.now(timezone.utc)
                    if (now - health.last_heartbeat).total_seconds() > health_policy.timeout_seconds:
                        raise Exception(f"Runtime heartbeat timeout ({health_policy.timeout_seconds}s elapsed).")
                        
                await asyncio.sleep(health_policy.interval_seconds)
                self._restart_attempts = 0 # Reset
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._publish(RuntimeFaultDetected(self._name, str(e), ""))
                
                restart_policy = self._metadata.restart_policy
                if restart_policy in [RestartPolicy.ALWAYS, RestartPolicy.ON_FAILURE]:
                    self._restart_attempts += 1
                    if self._restart_attempts > health_policy.max_retries:
                        self._is_supervising = False
                        self._publish(RuntimeStateChanged(self._name, self._runtime.get_state().name, RuntimeState.FAILED.name, "Max retries exceeded"))
                        break
                    else:
                        self._publish(RuntimeStateChanged(self._name, self._runtime.get_state().name, RuntimeState.RESTARTING.name, "Attempting recovery"))
                        try:
                            await self.restart_runtime()
                        except Exception as recovery_err:
                            self._publish(RuntimeFaultDetected(self._name, f"Recovery failed: {recovery_err}", ""))
                else:
                    self._is_supervising = False
                    self._publish(RuntimeStateChanged(self._name, self._runtime.get_state().name, RuntimeState.FAILED.name, "RestartPolicy prevents recovery"))
                    break
