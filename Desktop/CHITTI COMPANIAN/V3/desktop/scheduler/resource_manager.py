import time
import uuid
from typing import List, Dict, Optional
from desktop.scheduler.interfaces import IResourceArbitrator, ResourceAcquireResult
from desktop.scheduler.models import ResourceLock, SchedulerPolicy
from desktop.execution_graph.models import ResourceRequirement, ResourceAccessMode

class ResourceManager(IResourceArbitrator):
    def __init__(self, policy: SchedulerPolicy):
        self.policy = policy
        self._active_locks: Dict[str, ResourceLock] = {}
        # Keys are lock_id

    async def acquire(self, workflow_id: str, execution_id: str, node_id: str, resources: List[ResourceRequirement], priority: int) -> ResourceAcquireResult:
        if not resources:
            return ResourceAcquireResult(success=True)

        # 1. Global Deterministic Sorting (Deadlock Prevention)
        # Always acquire resources in alphabetical order by resource_id
        sorted_reqs = sorted(resources, key=lambda r: r.resource)

        # 2. Check Availability (All-or-Nothing)
        blocked_resources = []
        for req in sorted_reqs:
            if self._is_resource_busy(req.resource, req.mode):
                blocked_resources.append(req.resource)

        if blocked_resources:
            # Atomic failure - grant nothing.
            return ResourceAcquireResult(
                success=False,
                blocked_resources=blocked_resources,
                reason="Resources currently held by other workflows."
            )

        # 3. Grant Locks
        granted_locks = []
        now = time.time()
        for req in sorted_reqs:
            lock = ResourceLock(
                lock_id=str(uuid.uuid4()),
                workflow_id=workflow_id,
                execution_id=execution_id,
                node_id=node_id,
                resource_id=req.resource,
                acquired_at=now,
                expires_at=now + req.timeout,
                priority=priority
            )
            self._active_locks[lock.lock_id] = lock
            granted_locks.append(lock)

        return ResourceAcquireResult(success=True, granted_resources=granted_locks)

    def release_all(self, workflow_id: str):
        # Only ResourceManager may manipulate locks.
        locks_to_remove = [l_id for l_id, l in self._active_locks.items() if l.workflow_id == workflow_id]
        for l_id in locks_to_remove:
            del self._active_locks[l_id]

    def _is_resource_busy(self, resource_id: str, mode: ResourceAccessMode) -> bool:
        # Simplified for Sprint 5.3 structure. Real implementation would check 
        # existing locks against SHARED/EXCLUSIVE modes.
        for lock in self._active_locks.values():
            if lock.resource_id == resource_id:
                # If there's any lock and mode is EXCLUSIVE, or existing lock is EXCLUSIVE
                # (For now assuming all are EXCLUSIVE to simulate busy state)
                return True
        return False
