from typing import Any, Dict, List, Optional

from desktop.platform.shared.interfaces.artifact_store import IArtifactStore
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.artifact import Artifact


class ArtifactStore(IArtifactStore):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._store: Dict[str, Artifact] = {}

    @property
    def name(self) -> str: return "ArtifactStore"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info("ArtifactStore initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> Dict[str, Any]:
        return {"artifacts_count": len(self._store)}

    def store_artifact(self, artifact: Artifact) -> None:
        if artifact.id in self._store:
            raise ValueError(f"Artifact {artifact.id} already exists. Artifacts are immutable.")
        self._store[artifact.id] = artifact
        self.logger.info(f"Stored {artifact.type} ({artifact.id})")

    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        return self._store.get(artifact_id)

    def get_all_artifacts(self) -> List[Artifact]:
        return list(self._store.values())
