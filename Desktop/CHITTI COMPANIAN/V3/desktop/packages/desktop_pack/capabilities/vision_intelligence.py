from typing import List, Dict, Any
from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.models.capability import (
    ExecutionResult, CanonicalCapabilityOutput, VerificationResult, 
    PresentationDescriptor, MemoryCandidate
)
from desktop.models.conversation import ErrorArtifact, TableArtifact, DocumentArtifact, ApplicationArtifact
from datetime import datetime
import os
import uuid
import tempfile
try:
    from PIL import ImageGrab
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def _mock_canonical(payload: Dict[str, Any], artifact_instance: Any = None) -> CanonicalCapabilityOutput:
    return CanonicalCapabilityOutput(
        execution_result=ExecutionResult(success=True, payload=payload),
        verification_result=VerificationResult(verified=True, evidence_ids=[], verification_strategy="mock_vision"),
        conversation_artifact=artifact_instance,
        presentation_descriptor=PresentationDescriptor(experience_id="vision_exp", recipe_id="recipe_vision_overlay", layout_data={}),
        memory_candidate=MemoryCandidate(activity_type="Vision Check", workspace_hint="VisionWorkspace", related_entities=[])
    )

class VisionCaptureCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["vision_capture"]
    def describe(self) -> Dict[str, Any]: return {"name": "VisionCaptureCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        if not PIL_AVAILABLE:
            return _mock_canonical({"captured": False, "error": "Pillow (PIL) not installed. Screen capture unavailable."})
            
        try:
            region = invocation.arguments.get("region") if invocation.arguments else None
            bbox = None
            if region:
                bbox = (region.get("x", 0), region.get("y", 0), 
                        region.get("x", 0) + region.get("w", 1920), 
                        region.get("y", 0) + region.get("h", 1080))
            
            # Physical Screen Capture
            img = ImageGrab.grab(bbox=bbox)
            
            # In-memory payload
            payload = {"captured": True, "image_obj": img}
            
            # Only create temporary file if explicitly requested
            export_file = invocation.arguments.get("export_file", False) if invocation.arguments else False
            if export_file:
                temp_path = os.path.join(tempfile.gettempdir(), f"vision_capture_{uuid.uuid4().hex}.png")
                img.save(temp_path)
                payload["image_path"] = temp_path
                
            return _mock_canonical(payload)
            
        except OSError as e:
            # Deterministic failure for OS/Permission errors
            return _mock_canonical({"captured": False, "error": f"Capture failed (Permission or OS Error): {str(e)}"})
        except Exception as e:
            return _mock_canonical({"captured": False, "error": f"Capture failed: {str(e)}"})

class VisionLayoutCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["vision_layout"]
    def describe(self) -> Dict[str, Any]: return {"name": "VisionLayoutCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        print("[ExecutionRuntime] Analyzing pixels, generating VisionLayoutTree...")
        return _mock_canonical({"layout_tree": "MockVisionLayoutTree"})

class VisionErrorCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["vision_error"]
    def describe(self) -> Dict[str, Any]: return {"name": "VisionErrorCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        print("[ExecutionRuntime] Extracting error dialog from VisionLayoutTree. Emitting ErrorArtifact.")
        art = ErrorArtifact(
            artifact_id="art_err", artifact_type="ErrorArtifact", capability_id="VisionErrorCapability",
            timestamp=datetime.now(), summary="Compilation Error", structured_result={}, referenced_entities=[],
            source_window="VS Code", capture_timestamp=datetime.now(), vision_layout_tree_id="v_1",
            error_message="NullReferenceException at line 42", error_context="Editor", bounding_box={"x":10,"y":10,"w":100,"h":50}
        )
        return _mock_canonical({"error": True}, artifact_instance=art)

class VisionTableCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["vision_table"]
    def describe(self) -> Dict[str, Any]: return {"name": "VisionTableCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        print("[ExecutionRuntime] Extracting tabular grid from VisionLayoutTree. Emitting TableArtifact.")
        art = TableArtifact(
            artifact_id="art_tab", artifact_type="TableArtifact", capability_id="VisionTableCapability",
            timestamp=datetime.now(), summary="Financial Data", structured_result={}, referenced_entities=[],
            source_window="Excel", capture_timestamp=datetime.now(), vision_layout_tree_id="v_2",
            headers=["Q1", "Q2"], rows=[["100", "200"]], bounding_box={"x":0,"y":0,"w":500,"h":500}
        )
        return _mock_canonical({"table": True}, artifact_instance=art)

class VisionDocumentCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["vision_document"]
    def describe(self) -> Dict[str, Any]: return {"name": "VisionDocumentCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        print("[ExecutionRuntime] Extracting paragraphs from VisionLayoutTree. Emitting DocumentArtifact.")
        art = DocumentArtifact(
            artifact_id="art_doc", artifact_type="DocumentArtifact", capability_id="VisionDocumentCapability",
            timestamp=datetime.now(), summary="PDF Document", structured_result={}, referenced_entities=[],
            source_window="Acrobat", capture_timestamp=datetime.now(), vision_layout_tree_id="v_3", knowledge=None
        )
        return _mock_canonical({"document": True}, artifact_instance=art)

class VisionControlCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["vision_control"]
    def describe(self) -> Dict[str, Any]: return {"name": "VisionControlCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        print("[ExecutionRuntime] Extracting UI affordances from VisionLayoutTree. Emitting ApplicationArtifact.")
        art = ApplicationArtifact(
            artifact_id="art_app", artifact_type="ApplicationArtifact", capability_id="VisionControlCapability",
            timestamp=datetime.now(), summary="Settings UI", structured_result={}, referenced_entities=[],
            source_window="Settings", capture_timestamp=datetime.now(), vision_layout_tree_id="v_4", ui_controls={"Submit": {"x":10, "y":20, "w":50, "h":20}}
        )
        return _mock_canonical({"controls": True}, artifact_instance=art)
