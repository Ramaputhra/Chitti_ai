from typing import List, Callable, Dict, Set
import asyncio
from dataclasses import dataclass

from desktop.core.supervisor import IRuntimeSupervisor, BaseRuntimeSupervisor
from desktop.core.runtime import IRuntime
from desktop.models.events import SystemEvent

# --- Application Core Events ---

@dataclass
class ApplicationCoreStarting(SystemEvent):
    event_type: str = "ApplicationCoreStarting"

@dataclass
class ApplicationCoreReady(SystemEvent):
    event_type: str = "ApplicationCoreReady"

@dataclass
class ApplicationCoreShuttingDown(SystemEvent):
    event_type: str = "ApplicationCoreShuttingDown"

@dataclass
class ApplicationCorePanic(SystemEvent):
    event_type: str = "ApplicationCorePanic"
    reason: str = ""

# --- Dependency Resolver ---

class DependencyResolver:
    """
    Sorts runtime dependencies (DAG) for startup.
    1. Topological Order (Dependencies first)
    2. Priority (Fallback for independent runtimes)
    3. Registration Order (Final tie-breaker)
    """
    def sort_supervisors(self, supervisors: List[IRuntimeSupervisor]) -> List[IRuntimeSupervisor]:
        sup_by_id = {sup.get_runtime_id(): sup for sup in supervisors}
        
        # Build DAG
        in_degree: Dict[str, int] = {sup_id: 0 for sup_id in sup_by_id}
        adj_list: Dict[str, List[str]] = {sup_id: [] for sup_id in sup_by_id}
        
        for sup_id, sup in sup_by_id.items():
            deps = sup.get_supervised_runtime().get_metadata().dependencies
            for dep_id in deps:
                if dep_id not in sup_by_id:
                    raise RuntimeError(f"Runtime '{sup_id}' depends on '{dep_id}' which is not registered.")
                # dep_id -> sup_id
                adj_list[dep_id].append(sup_id)
                in_degree[sup_id] += 1
                
        # Find initial zero-degree nodes
        zero_in_degree = [sup_id for sup_id, degree in in_degree.items() if degree == 0]
        
        # Original indices for tie-breaking
        orig_index = {sup.get_runtime_id(): idx for idx, sup in enumerate(supervisors)}
        
        sorted_sup_ids = []
        
        while zero_in_degree:
            # Sort zero_in_degree by Priority (asc), then by Original Registration Index (asc)
            zero_in_degree.sort(key=lambda sid: (
                sup_by_id[sid].get_supervised_runtime().get_metadata().priority.value,
                orig_index[sid]
            ))
            
            # Pop the first element
            curr_id = zero_in_degree.pop(0)
            sorted_sup_ids.append(curr_id)
            
            for neighbor_id in adj_list[curr_id]:
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    zero_in_degree.append(neighbor_id)
                    
        if len(sorted_sup_ids) != len(supervisors):
            raise RuntimeError("Dependency cycle detected among runtimes.")
            
        return [sup_by_id[sid] for sid in sorted_sup_ids]

# --- Application Core ---

class ApplicationCore:
    """
    The central orchestrator managing startup/shutdown sequencing and global error handling.
    """
    def __init__(self, event_publisher: Callable[[SystemEvent], None]):
        self._supervisors: List[IRuntimeSupervisor] = []
        self._resolver = DependencyResolver()
        self._publish = event_publisher
        self._is_running = False

    def register_runtime(self, runtime: IRuntime) -> None:
        """Dynamically wraps the runtime in a Supervisor and assigns the EventBus."""
        if self._is_running:
            raise RuntimeError("Cannot register runtimes after boot sequence has started.")
            
        # Core owns supervisor creation and event bus distribution
        supervisor = BaseRuntimeSupervisor(runtime, self._publish)
        self._supervisors.append(supervisor)

    async def boot(self) -> None:
        """Executes the Boot Sequence based on true dependency sorting."""
        self._publish(ApplicationCoreStarting())
        self._is_running = True

        try:
            sorted_sups = self._resolver.sort_supervisors(self._supervisors)
            for sup in sorted_sups:
                await sup.start_supervision()
            
            self._publish(ApplicationCoreReady())
        except Exception as e:
            self._publish(ApplicationCorePanic(reason=str(e)))
            await self.shutdown()
            raise

    async def shutdown(self) -> None:
        """Gracefully teardown supervisors in reverse-dependency order."""
        self._publish(ApplicationCoreShuttingDown())
        
        try:
            sorted_sups = self._resolver.sort_supervisors(self._supervisors)
            for sup in reversed(sorted_sups):
                try:
                    await sup.stop_supervision()
                except Exception as e:
                    self._publish(ApplicationCorePanic(reason=f"Failed to stop {sup.get_runtime_id()}: {e}"))
        except RuntimeError:
            # If DAG sorting fails during shutdown (should not happen if boot succeeded), fallback to reverse registration
            for sup in reversed(self._supervisors):
                try:
                    await sup.stop_supervision()
                except Exception:
                    pass
        
        self._is_running = False
