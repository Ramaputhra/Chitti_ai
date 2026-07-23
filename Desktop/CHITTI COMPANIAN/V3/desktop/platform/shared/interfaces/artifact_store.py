from typing import List, Optional

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.artifact import Artifact


class IArtifactStore(IService):
    """
    Immutable storage for all Artifacts. Artifacts should never be overwritten.
    New versions create new artifacts and are linked via the RelationshipEngine.
    """
    def store_artifact(self, artifact: Artifact) -> None:
        ...

    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        ...

    def get_all_artifacts(self) -> List[Artifact]:
        ...
