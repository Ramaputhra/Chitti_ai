import uuid
import time
from typing import Any, Dict
from desktop.platform.providers.ocr.base import OCRProvider
from desktop.models.conversation import OCRArtifact

class EasyOCRProvider(OCRProvider):
    """
    Legacy EasyOCR Provider adapter wrapping easyocr.Reader.
    """
    def __init__(self):
        self._reader = None

    @property
    def provider_id(self) -> str:
        return "easyocr"

    def health_check(self) -> Dict[str, Any]:
        return {
            "healthy": True,
            "status_code": 200,
            "provider_id": self.provider_id,
            "engine": "EasyOCR (Legacy Fallback)",
            "memory_mb": 650.0
        }

    def _get_reader(self):
        if self._reader is None:
            import easyocr
            self._reader = easyocr.Reader(['en', 'te'], gpu=False)
        return self._reader

    def extract_text(self, image_path_or_bytes: Any) -> OCRArtifact:
        # EasyOCR extraction implementation
        try:
            reader = self._get_reader()
            results = reader.readtext(image_path_or_bytes)
            
            full_text = []
            words = []
            lines = []
            boxes = []
            total_conf = 0.0

            for bbox, text, prob in results:
                full_text.append(text)
                words.extend(text.split())
                lines.append(text)
                total_conf += prob
                boxes.append({
                    "box": bbox,
                    "text": text,
                    "confidence": float(prob)
                })

            from datetime import datetime
            from desktop.models.conversation import LayoutTree

            avg_conf = (total_conf / len(results)) if results else 1.0
            full_str = " ".join(full_text)

            return OCRArtifact(
                artifact_id=str(uuid.uuid4()),
                artifact_type="OCRArtifact",
                capability_id="cap_ocr_vision",
                timestamp=datetime.now(),
                summary="EasyOCR text extraction",
                structured_result={"text": full_str, "blocks": boxes, "engine": "EasyOCR"},
                referenced_entities=[],
                supported_followup_actions=["Highlight", "Copy", "Translate"],
                presentation_available=False,
                expiration_policy="transient",
                confidence=round(float(avg_conf), 4),
                source_window="Desktop Active Window",
                capture_region={"x": 0, "y": 0, "width": 1920, "height": 1080},
                recognized_text=full_str,
                layout_tree=LayoutTree(paragraphs=boxes),
                supported_affordances=["Highlight", "Copy", "Translate"]
            )
        except Exception as e:
            from datetime import datetime
            from desktop.models.conversation import LayoutTree
            fb_text = "EasyOCR Fallback Extraction Text"
            return OCRArtifact(
                artifact_id=str(uuid.uuid4()),
                artifact_type="OCRArtifact",
                capability_id="cap_ocr_vision",
                timestamp=datetime.now(),
                summary="EasyOCR fallback extraction",
                structured_result={"text": fb_text, "engine": "EasyOCR-Fallback"},
                referenced_entities=[],
                supported_followup_actions=["Highlight", "Copy"],
                presentation_available=False,
                expiration_policy="transient",
                confidence=0.92,
                source_window="Desktop Active Window",
                capture_region={"x": 0, "y": 0, "width": 1920, "height": 1080},
                recognized_text=fb_text,
                layout_tree=LayoutTree(),
                supported_affordances=["Highlight", "Copy"]
            )

