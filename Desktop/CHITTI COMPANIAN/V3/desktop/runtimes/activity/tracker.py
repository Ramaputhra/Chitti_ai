import time
import uuid
import datetime
from typing import Dict, Any, List, Optional
from desktop.models.companion import ActivityMemoryModel
from desktop.runtimes.activity.observers.vscode_observer import VSCodeObserver
from desktop.runtimes.activity.observers.node_observer import NodeObserver
from desktop.runtimes.activity.observers.git_observer import GitObserver

import asyncio
from desktop.models.lifecycle import IRuntime
from desktop.app.context import KernelContext

class ActivityTrackerRuntime(IRuntime):
    """
    The background runtime capturing activity.
    Flow: OS Events -> Normalizer -> Activity Snapshot -> MemoryRuntime.
    """
    def __init__(self, memory_runtime=None):
        self.memory_runtime = memory_runtime
        self.memory_runtime = memory_runtime
        self.vscode_observer = VSCodeObserver()
        self.node_observer = NodeObserver()
        self.git_observer = GitObserver()
        self._running = False
        self._task = None

    @property
    def dependencies(self):
        return []

    async def initialize(self, context: KernelContext) -> bool:
        if not self.memory_runtime:
            from desktop.app.memory_contracts import IMemoryService
            self.memory_runtime = context.registry.get(IMemoryService)
        return True

    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._loop())
        return True

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
        return True

    def health(self):
        from desktop.models.lifecycle import HealthState
        return HealthState.HEALTHY

    async def shutdown(self) -> bool:
        await self.stop()
        return True

    async def _loop(self):
        while self._running:
            await self.capture_snapshot()
            await asyncio.sleep(10.0)

        
    async def capture_snapshot(self) -> Optional[ActivityMemoryModel]:
        from desktop.models.companion import ObserverStatus, ActivityState
        
        observer_health = []
        
        # 1. Start with VS Code (our anchor for workspace)
        try:
            base_data = self.vscode_observer.observe()
            observer_health.append(ObserverStatus("VSCodeObserver", True, "OK"))
        except Exception as e:
            base_data = None
            observer_health.append(ObserverStatus("VSCodeObserver", False, str(e)))
            
        if not base_data:
            return None
            
        workspace = base_data.get("workspace_path")
        
        # 2. Augment with Node info
        try:
            node_data = self.node_observer.observe(workspace) or {}
            observer_health.append(ObserverStatus("NodeObserver", True, "OK"))
        except Exception as e:
            node_data = {}
            observer_health.append(ObserverStatus("NodeObserver", False, str(e)))
        
        # 3. Augment with Git info
        try:
            git_data = self.git_observer.observe(workspace) or {}
            observer_health.append(ObserverStatus("GitObserver", True, "OK"))
        except Exception as e:
            git_data = {}
            observer_health.append(ObserverStatus("GitObserver", False, str(e)))
        
        # 4. Construct Genuine ActivityMemoryModel
        snapshot = ActivityMemoryModel(
            activity_id=f"act_{uuid.uuid4().hex[:8]}",
            domain="Coding",
            application=base_data.get("application", "VS Code"),
            workspace_path=workspace,
            project_name=base_data.get("project_name", "Unknown"),
            launch_command=node_data.get("launch_command", "npm"),
            readiness=node_data.get("readiness", "port: 5173, expected_status: 200"),
            browser_url=node_data.get("browser_url", "http://localhost:5173"),
            git_branch=git_data.get("git_branch", "main"),
            last_active=datetime.datetime.utcnow(),
            resume_priority=1,
            verification={"source": "psutil"},
            state=ActivityState.ACTIVE,
            resume_confidence=1.0,
            observer_health=observer_health,
            schema_version=1
        )
        
        # 5. Persist to MemoryRuntime if provided
        if self.memory_runtime:
            await self.memory_runtime.commit_activity(snapshot)
            
        return snapshot

