from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class ReadinessVerification:
    port: int
    http_path: str = "/"
    expected_status: int = 200
    content_signature: Optional[str] = None

@dataclass
class ResumeMetrics:
    restore_time: float = 0.0
    verification_time: float = 0.0
    recovery_count: int = 0
    startup_time: float = 0.0
    readiness_score: float = 0.0
    completed: bool = False

@dataclass
class DevelopmentProfile:
    """
    Defines the physical characteristics of a local development workspace.
    Consumed by the ResumeActivityOrchestrator to launch, verify, and restore a session.
    """
    profile_name: str
    workspace_path: str
    editor_command: str = "code"
    editor_args: List[str] = field(default_factory=lambda: ["."])
    start_command: str = "npm"
    start_args: List[str] = field(default_factory=lambda: ["run", "dev"])
    startup_timeout_sec: int = 45
    launch_url: str = "http://localhost:5173"
    verification: Optional[ReadinessVerification] = None
    
    @classmethod
    def get_react_default(cls, path: str) -> "DevelopmentProfile":
        return cls(
            profile_name="React Development",
            workspace_path=path,
            editor_command="code",
            editor_args=["."],
            start_command="npm",
            start_args=["run", "dev"],
            startup_timeout_sec=45,
            launch_url="http://localhost:5173",
            verification=ReadinessVerification(
                port=5173,
                http_path="/",
                expected_status=200,
                content_signature='<div id="root">'
            )
        )
