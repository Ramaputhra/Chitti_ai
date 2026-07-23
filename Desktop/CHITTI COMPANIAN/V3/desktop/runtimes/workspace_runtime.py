import logging
import json
import os
from typing import Dict, Any, List, Optional

from desktop.models.lifecycle import IRuntime, HealthState
from desktop.app.context import KernelContext
from desktop.models.workspace import WorkspaceProfile

logger = logging.getLogger(__name__)

class WorkspaceRuntime(IRuntime):
    """
    Sprint 7.3: Workspace Runtime.
    Manages structured environment profiles to prepare context for the user.
    """
    def __init__(self, profiles_dir: str = "workspaces"):
        self.context: Optional[KernelContext] = None
        self._running = False
        self._profiles_dir = profiles_dir
        self._workspaces: Dict[str, WorkspaceProfile] = {}

    @property
    def dependencies(self) -> List[Any]:
        return []

    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        # In a real scenario, this would be an absolute path in AppData
        if not os.path.exists(self._profiles_dir):
            try:
                os.makedirs(self._profiles_dir, exist_ok=True)
            except Exception as e:
                logger.warning(f"Could not create workspaces dir: {e}")
        return True

    async def start(self) -> bool:
        self._running = True
        self._load_profiles()
        logger.info(f"WorkspaceRuntime started with {len(self._workspaces)} profiles.")
        return True

    async def stop(self) -> bool:
        self._running = False
        return True

    def health(self) -> HealthState:
        return HealthState.HEALTHY

    async def shutdown(self) -> bool:
        return True

    def _load_profiles(self):
        if not os.path.exists(self._profiles_dir):
            return
            
        for filename in os.listdir(self._profiles_dir):
            if filename.endswith(".json"):
                path = os.path.join(self._profiles_dir, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        profile = WorkspaceProfile(
                            id=data.get("id", filename.replace(".json", "")),
                            name=data.get("name", "Unknown Workspace"),
                            applications=data.get("applications", []),
                            files=data.get("files", []),
                            folders=data.get("folders", []),
                            urls=data.get("urls", []),
                            environment_variables=data.get("environment_variables", {}),
                            startup_sequence=data.get("startup_sequence", []),
                            post_actions=data.get("post_actions", []),
                            tags=data.get("tags", [])
                        )
                        self._workspaces[profile.id] = profile
                except Exception as e:
                    logger.error(f"Failed to load workspace profile {filename}: {e}")

    def get_workspace(self, workspace_id: str) -> Optional[WorkspaceProfile]:
        return self._workspaces.get(workspace_id)

    def get_all_workspaces(self) -> List[WorkspaceProfile]:
        return list(self._workspaces.values())
        
    def find_workspaces_by_tag(self, tag: str) -> List[WorkspaceProfile]:
        return [w for w in self._workspaces.values() if tag in w.tags]
