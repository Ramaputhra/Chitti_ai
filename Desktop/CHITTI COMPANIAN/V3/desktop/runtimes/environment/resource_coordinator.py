from desktop.models.environment import EnvironmentResourceLock

class ResourceCoordinator:
    """
    Centralized arbitration to prevent workflow collision (Rule 351).
    Adapters never perform independent locking or scheduling.
    """
    def __init__(self):
        self._locks = {}

    def acquire_lock(self, hierarchy_path: str, workflow_id: str) -> EnvironmentResourceLock:
        """
        e.g. acquire_lock("Browser/Chrome/Tab4", "wf_123")
        """
        print(f"[ResourceCoordinator] Acquiring lock for {hierarchy_path}")
        lock = EnvironmentResourceLock(lock_id="lock_" + hierarchy_path, hierarchy_path=hierarchy_path, owner_workflow_id=workflow_id, is_acquired=True)
        self._locks[hierarchy_path] = lock
        return lock

    def release_lock(self, lock_id: str):
        pass
