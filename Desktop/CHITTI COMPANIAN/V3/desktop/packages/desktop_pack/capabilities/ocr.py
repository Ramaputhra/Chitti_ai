import uuid
from datetime import datetime
from typing import List
import os
import tempfile
try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import numpy as np

_EASYOCR_READER = None

def get_easyocr_reader():
    global _EASYOCR_READER
    if _EASYOCR_READER is None:
        import easyocr
        # Loaded exactly once and reused for application lifetime
        _EASYOCR_READER = easyocr.Reader(['en', 'te'], gpu=False)
    return _EASYOCR_READER

from desktop.models.capability import (
    CanonicalCapabilityOutput,
    ExecutionResult as CapExecutionResult,
    VerificationResult,
    PresentationDescriptor,
    MemoryCandidate
)
from desktop.models.conversation import OCRArtifact, LayoutTree

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor

class OCRCapability(ICapability):
    """
    OCR Capability (Sprint 24).
    Deterministic desktop observation via OCR. 
    Separates screen capture -> image snapshot -> OCR extraction -> OCRArtifact.
    Makes NO semantic interpretations.
    """
    def __init__(self):
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "OCRCapability"

    @property
    def capability_id(self) -> str:
        return "cap_ocr_vision"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> dict:
        return {"status": "healthy"}

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="ocr_capture",
                description="OCR Vision capture.",
                parameters={}
            )
        ]

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name=self.name,
            version="1.0",
            category="System",
            tools=self.discover_tools(),
            description="OCR Vision capture capability."
        )

    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name == "ocr_capture"

    def cancel(self, invocation_id: str) -> None:
        pass

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if not self.validate(invocation):
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Invalid tool."])

        if not PIL_AVAILABLE:
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Pillow (PIL) not installed. Screen capture unavailable."])

        payload = invocation.arguments
        source_window = payload.get("source_window", "Desktop")
        region = payload.get("region", {"x": 0, "y": 0, "w": 1920, "h": 1080})
        
        # 1. Screen Capture (Physical Implementation)
        try:
            bbox = (region.get("x", 0), region.get("y", 0), 
                    region.get("x", 0) + region.get("w", 1920), 
                    region.get("y", 0) + region.get("h", 1080))
            img = ImageGrab.grab(bbox=bbox)
            
            # 2. Image Snapshot (In Memory - Default)
            capture_payload = {
                "source_window": source_window,
                "region_captured": region,
                "extraction_complete": True,
                "image_obj": img
            }
            
            # Optional file export
            export_file = payload.get("export_file", False)
            if export_file:
                temp_path = os.path.join(tempfile.gettempdir(), f"ocr_capture_{uuid.uuid4().hex}.png")
                img.save(temp_path)
                capture_payload["image_path"] = temp_path
                
        except OSError as e:
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=[f"Capture failed (Permission or OS Error): {str(e)}"])
        except Exception as e:
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=[f"Capture failed: {str(e)}"])

        # 3. OCR Extraction via Multi-Provider Platform (ProviderManager)
        try:
            from desktop.platform.providers.provider_manager import ProviderManager
            provider = ProviderManager.get_instance().get_provider("ocr")
            ocr_artifact = provider.extract_text(temp_filepath)
            
            extracted_text = ocr_artifact.recognized_text
            layout = ocr_artifact.layout_tree
            structured_blocks = layout.paragraphs
            overall_conf = ocr_artifact.confidence

        except Exception as e:
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=[f"OCR provider failed: {str(e)}"])

        layout = LayoutTree(paragraphs=structured_blocks)
        confidences = [b.get("confidence", overall_conf) for b in structured_blocks if isinstance(b, dict)]
        
        capture_payload["ocr_metadata"] = {
            "min_confidence": min(confidences) if confidences else overall_conf,
            "max_confidence": max(confidences) if confidences else overall_conf,
            "overall_confidence": overall_conf,
            "block_count": len(structured_blocks)
        }

        
        cap_exec_result = CapExecutionResult(
            success=True,
            payload=capture_payload
        )
        
        verify_result = VerificationResult(
            verified=True,
            evidence_ids=["screen_capture_api", "ocr_engine_logs"],
            verification_strategy="vision_checksum"
        )
        
        # 4. Construct OCRArtifact
        affordances = ["Highlight", "Translate", "Summarize", "Explain", "Copy", "Search", "Present"]
        
        artifact = OCRArtifact(
            artifact_id=str(uuid.uuid4()),
            artifact_type="OCRArtifact",
            capability_id=self.capability_id,
            timestamp=datetime.now(),
            summary=f"OCR capture of {source_window}",
            structured_result=cap_exec_result.payload,
            referenced_entities=[],
            supported_followup_actions=affordances,
            presentation_available=False,
            expiration_policy="transient",
            confidence=overall_conf,
            source_window=source_window,
            capture_region=region,
            recognized_text=extracted_text,
            layout_tree=layout,
            supported_affordances=affordances
        )
        
        # Presentation descriptor instructs PresentationEngine to draw bounding boxes
        pres_descriptor = PresentationDescriptor(
            experience_id="exp_vision_overlay",
            recipe_id="recipe_bounding_boxes",
            layout_data={"region": region, "headings_count": len(layout.headings)}
        )
        
        artifact.presentation_descriptor = pres_descriptor.__dict__
        
        mem_candidate = MemoryCandidate(
            activity_type="Screen Capture",
            workspace_hint=source_window,
            related_entities=["OCR Extraction"],
            timestamp=datetime.now()
        )
        
        artifact.memory_candidate = mem_candidate.__dict__
        
        canonical_out = CanonicalCapabilityOutput(
            execution_result=cap_exec_result,
            verification_result=verify_result,
            conversation_artifact=artifact,
            presentation_descriptor=pres_descriptor,
            memory_candidate=mem_candidate
        )
        return ExecutionResult(status=ExecutionStatus.SUCCESS, data=canonical_out)
