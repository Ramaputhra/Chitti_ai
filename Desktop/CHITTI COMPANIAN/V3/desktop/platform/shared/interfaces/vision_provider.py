from typing import Any, Dict

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.vision_artifact import VisionArtifact


class IVisionProvider(IService):
    """
    Standard interface for all Vision capabilities.
    Maintains the CHITTI architecture standard for providers.
    """
    def detect(self, preprocessed_image: bytes) -> VisionArtifact:
        """Processes the normalized image and yields a specific VisionArtifact."""
        ...

    def describe(self) -> Dict[str, Any]:
        """Returns metadata about the provider's capabilities."""
        ...

    def supports(self, modality: str) -> bool:
        """Determines if the provider can handle the requested visual modality."""
        ...

    def benchmark(self) -> Dict[str, float]:
        """Measures latency and confidence averages for diagnostics."""
        ...
