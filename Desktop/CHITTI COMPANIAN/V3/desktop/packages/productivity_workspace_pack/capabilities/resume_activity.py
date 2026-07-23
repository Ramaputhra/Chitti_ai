from typing import Dict, Any
from desktop.packages.sdk.pack_metadata import CapabilityMetadata
from desktop.packages.productivity_workspace_pack.orchestrators.resume_activity import ResumeActivityOrchestrator
from desktop.packages.productivity_workspace_pack.models.profile import DevelopmentProfile, ReadinessVerification

class ResumeActivityCapability:
    """
    Wraps the ResumeActivityOrchestrator into a standard Capability 
    that the ExecutionRuntime can invoke.
    """
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Productivity")
        
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Executes the Orchestrator using the provided development profile path.
        """
        verif = None
        if "verification" in kwargs:
            v_data = kwargs["verification"]
            verif = ReadinessVerification(
                port=v_data.get("port"),
                http_path=v_data.get("http_path", "/"),
                expected_status=v_data.get("expected_status", 200),
                content_signature=v_data.get("content_signature")
            )
            
        profile = DevelopmentProfile(
            profile_name=kwargs.get("profile_name", "Unknown Project"),
            workspace_path=kwargs.get("workspace_path", "."),
            editor_command=kwargs.get("editor_command", "code"),
            editor_args=kwargs.get("editor_args", ["."]),
            start_command=kwargs.get("start_command", "npm"),
            start_args=kwargs.get("start_args", ["run", "dev"]),
            startup_timeout_sec=kwargs.get("startup_timeout_sec", 45),
            launch_url=kwargs.get("launch_url", "http://localhost"),
            verification=verif
        )
        
        # Instantiate and run the Orchestrator
        orchestrator = ResumeActivityOrchestrator(profile)
        
        # In a real environment, this might be asynchronous. For V0.1 we block.
        checkpoint = orchestrator.execute()
        
        return {
            "status": "completed",
            "checkpoint_id": checkpoint.checkpoint_id
        }
