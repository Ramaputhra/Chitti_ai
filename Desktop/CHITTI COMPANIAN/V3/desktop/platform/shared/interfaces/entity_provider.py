from typing import List

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.artifact import Artifact
from desktop.platform.shared.models.knowledge import Entity


class IEntityProvider(IService):
    """
    Abstract interface for Entity Extraction.
    Can be implemented by spaCy, GLiNER, Regex, LLM, or Vision providers.
    """
    def extract_entities(self, artifact: Artifact) -> List[Entity]:
        ...
