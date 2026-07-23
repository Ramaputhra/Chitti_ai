import unittest
import asyncio
from datetime import datetime, timezone
from typing import List

from desktop.core.runtime import (
    IRuntime, RuntimeMetadata, RuntimeState, RuntimePriority, RestartPolicy,
    RuntimeTraits, HealthPolicy, HealthPayload
)
from desktop.core.supervisor import BaseRuntimeSupervisor
from desktop.core.application import DependencyResolver, ApplicationCore

class DummyRuntime(IRuntime):
    def __init__(self, metadata: RuntimeMetadata):
        self._metadata = metadata
        self._state = RuntimeState.CREATED
        self._health = HealthPayload(True, self._state, datetime.now(timezone.utc), 0.0)
    
    def get_metadata(self) -> RuntimeMetadata:
        return self._metadata
        
    def get_state(self) -> RuntimeState:
        return self._state
        
    async def initialize(self) -> None:
        self._state = RuntimeState.READY
        
    async def start(self) -> None:
        self._state = RuntimeState.RUNNING
        
    async def stop(self) -> None:
        self._state = RuntimeState.STOPPED
        
    async def health_check(self) -> HealthPayload:
        self._health.state = self._state
        self._health.last_heartbeat = datetime.now(timezone.utc)
        return self._health
        
    def force_health(self, healthy: bool):
        self._health.healthy = healthy

class TestDependencyResolver(unittest.TestCase):
    def test_topological_sort(self):
        def make_sup(idx: str, deps: List[str], prio: int):
            meta = RuntimeMetadata(idx, "1.0", RuntimePriority(prio), deps, RuntimeTraits(), HealthPolicy(), RestartPolicy.NEVER)
            return BaseRuntimeSupervisor(DummyRuntime(meta), lambda e: None)
            
        supA = make_sup("A", ["B", "C"], 4)
        supB = make_sup("B", ["C"], 3)
        supC = make_sup("C", ["D"], 2)
        supD = make_sup("D", [], 1)
        
        resolver = DependencyResolver()
        sorted_sups = resolver.sort_supervisors([supA, supB, supC, supD])
        ids = [s.get_runtime_id() for s in sorted_sups]
        self.assertEqual(ids, ["D", "C", "B", "A"])

    def test_cycle_detection(self):
        def make_sup(idx: str, deps: List[str]):
            meta = RuntimeMetadata(idx, "1.0", RuntimePriority.NORMAL, deps, RuntimeTraits(), HealthPolicy(), RestartPolicy.NEVER)
            return BaseRuntimeSupervisor(DummyRuntime(meta), lambda e: None)
            
        supA = make_sup("A", ["B"])
        supB = make_sup("B", ["A"])
        resolver = DependencyResolver()
        
        with self.assertRaises(RuntimeError):
            resolver.sort_supervisors([supA, supB])

class TestSupervisor(unittest.IsolatedAsyncioTestCase):
    async def test_supervisor_initialization_and_stop(self):
        meta = RuntimeMetadata("T1", "1.0", RuntimePriority.NORMAL, [], RuntimeTraits(), HealthPolicy(0.1, 1.0, 1), RestartPolicy.NEVER)
        runtime = DummyRuntime(meta)
        events = []
        sup = BaseRuntimeSupervisor(runtime, lambda e: events.append(e))
        
        await sup.start_supervision()
        self.assertEqual(runtime.get_state(), RuntimeState.RUNNING)
        await sup.stop_supervision()
        self.assertEqual(runtime.get_state(), RuntimeState.STOPPED)
        
    async def test_supervisor_restart_never(self):
        meta = RuntimeMetadata("T2", "1.0", RuntimePriority.NORMAL, [], RuntimeTraits(), HealthPolicy(0.1, 1.0, 1), RestartPolicy.NEVER)
        runtime = DummyRuntime(meta)
        sup = BaseRuntimeSupervisor(runtime, lambda e: None)
        
        await sup.start_supervision()
        runtime.force_health(False)
        await asyncio.sleep(0.3)
        # Should drop supervision
        self.assertFalse(sup._is_supervising)
        await sup.stop_supervision()
        
    async def test_supervisor_restart_on_failure(self):
        meta = RuntimeMetadata("T3", "1.0", RuntimePriority.NORMAL, [], RuntimeTraits(), HealthPolicy(0.1, 1.0, 1), RestartPolicy.ON_FAILURE)
        runtime = DummyRuntime(meta)
        sup = BaseRuntimeSupervisor(runtime, lambda e: None)
        
        await sup.start_supervision()
        runtime.force_health(False)
        await asyncio.sleep(0.3)
        # It should try to restart. If it stays unhealthy it eventually gives up.
        # Since it exceeded max_retries(1), it should drop supervision.
        self.assertFalse(sup._is_supervising)
        await sup.stop_supervision()

class TestApplicationCore(unittest.IsolatedAsyncioTestCase):
    async def test_boot_sequence(self):
        core = ApplicationCore(lambda e: None)
        meta = RuntimeMetadata("A1", "1.0", RuntimePriority.NORMAL, [], RuntimeTraits(), HealthPolicy(0.1, 1.0, 1), RestartPolicy.NEVER)
        runtime = DummyRuntime(meta)
        core.register_runtime(runtime)
        
        await core.boot()
        self.assertTrue(core._is_running)
        self.assertEqual(runtime.get_state(), RuntimeState.RUNNING)
        
        await core.shutdown()
        self.assertFalse(core._is_running)
        self.assertEqual(runtime.get_state(), RuntimeState.STOPPED)

if __name__ == '__main__':
    unittest.main()
