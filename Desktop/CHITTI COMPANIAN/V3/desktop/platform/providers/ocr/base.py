from abc import abstractmethod
from typing import Any
from desktop.platform.providers.base import BaseProvider
from desktop.models.conversation import OCRArtifact

class OCRProvider(BaseProvider):
    """
    Abstract Base Class for all OCR Providers.
    Output MUST strictly conform to canonical OCRArtifact model.
    """
    @property
    def category(self) -> str:
        return "ocr"

    @abstractmethod
    def extract_text(self, image_path_or_bytes: Any) -> OCRArtifact:
        """
        Extracts text and bounding boxes from an image,
        returning a canonical OCRArtifact object.
        """
        pass
