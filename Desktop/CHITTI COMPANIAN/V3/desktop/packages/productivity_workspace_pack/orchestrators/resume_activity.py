import time
from typing import Optional, Dict, Any

from desktop.models.companion import ActivityMemoryModel, CompanionState, ExecutionCheckpoint
from desktop.packages.desktop_pack.capabilities.execution import LaunchApplicationCapability, ExecuteTerminalCommandCapability, VerifyServiceReadinessCapability
from desktop.packages.productivity_workspace_pack.models.profile import DevelopmentProfile, ResumeMetrics

class ResumeActivityOrchestrator:
    """
    Executes a DevelopmentProfile physically on the Windows Desktop.
    Streams live progress, captures verification evidence, and defers narration to Behavior Runtime.
    """
    def __init__(self, profile: DevelopmentProfile):
        self.profile = profile
        self.state = CompanionState.PREPARING
        self.checkpoint: Optional[ExecutionCheckpoint] = None
        self._is_cancelled = False
        
        self.launcher = LaunchApplicationCapability()
        self.terminal = ExecuteTerminalCommandCapability()
        self.verifier = VerifyServiceReadinessCapability()
        self.metrics = ResumeMetrics()
        
    def cancel(self):
        self._is_cancelled = True
        self._emit_behavior_event("ResumeCancelled")
        print("[Orchestrator] Cancellation requested.")
        
    def execute(self) -> ExecutionCheckpoint:
        print(f"Starting Resume Activity for Profile: {self.profile.profile_name}")
        self._emit_behavior_event("ResumeStarted")
        start_time = time.time()
        
        # Preflight Check via Verifier
        required_tools = [self.profile.editor_command, self.profile.start_command]
        preflight_result = self.verifier.execute(
            workspace_path=self.profile.workspace_path,
            required_tools=required_tools
        )
        if not preflight_result.get("is_ready") and preflight_result.get("recovery"):
            self.metrics.recovery_count += 1
            self.metrics.completed = False
            self.metrics.restore_time = time.time() - start_time
            self._emit_behavior_event("RecoveryRequested", {"recovery": preflight_result.get("recovery")})
            return self._save_checkpoint()
        
        self._emit_behavior_event("EnvironmentPrepared")
        
        # Step 1: Open Editor
        self._stream_progress(f"Opening {self.profile.editor_command}")
        editor_result = self.launcher.execute(
            self.profile.editor_command, 
            self.profile.editor_args, 
            cwd=self.profile.workspace_path
        )
        if self._check_cancel_or_fail(editor_result, "Editor Launch"): return self._save_checkpoint()
        self._record_evidence(f"Editor Launched (PID {editor_result.get('pid')})")
        self._emit_behavior_event("WorkspaceOpened")

        # Step 2: Start Dev Server
        self._stream_progress(f"Starting {self.profile.start_command} server")
        self._emit_behavior_event("ServerStarting")
        srv_start = time.time()
        terminal_result = self.terminal.execute(
            self.profile.start_command, 
            self.profile.start_args, 
            cwd=self.profile.workspace_path
        )
        if self._check_cancel_or_fail(terminal_result, "Terminal Server"): return self._save_checkpoint()
        server_pid = terminal_result.get("pid")
        self._record_evidence(f"Server Started (PID {server_pid})")
        self.metrics.startup_time = time.time() - srv_start

        # Step 3: Deep Verification (Timeout loop)
        self.state = CompanionState.WAITING
        self._stream_progress(f"Waiting for {self.profile.launch_url}")
        
        timeout_sec = self.profile.startup_timeout_sec
        verif_start = time.time()
        is_ready = False
        
        verify_args = {"pid": server_pid}
        if self.profile.verification:
            verify_args["port"] = self.profile.verification.port
            verify_args["http_url"] = self.profile.launch_url
            verify_args["content_signature"] = self.profile.verification.content_signature
            verify_args["expected_status"] = self.profile.verification.expected_status
            
        while time.time() - verif_start < timeout_sec:
            if self._is_cancelled:
                return self._save_checkpoint()
                
            verify_result = self.verifier.execute(**verify_args)
            
            if verify_result.get("is_ready"):
                is_ready = True
                self.metrics.readiness_score = verify_result.get("readiness_score", 100)
                for ev in verify_result.get("evidence", []):
                    self._record_evidence(f"Verified: {ev}")
                break
                
            time.sleep(2.0) # Poll interval
            
        self.metrics.verification_time = time.time() - verif_start
            
        if not is_ready:
            self._handle_timeout(timeout_sec)
            return self._save_checkpoint()
            
        self._stream_progress("Server ready")
        self._emit_behavior_event("ServerReady")
        
        # Step 4: Open Browser
        self._stream_progress("Opening browser")
        browser_result = self.launcher.execute(
            "start", [self.profile.launch_url], cwd=self.profile.workspace_path
        )
        if self._check_cancel_or_fail(browser_result, "Browser Launch"): return self._save_checkpoint()
        self._emit_behavior_event("BrowserOpened")
        
        # 5. Completed
        self.metrics.completed = True
        self.metrics.restore_time = time.time() - start_time
        self.state = CompanionState.COMPLETED
        
        self._stream_progress("Session restored")
        
        # Render presentation payload
        presentation_data = {
            "Project": self.profile.profile_name,
            "Server": "Running",
            "URL": self.profile.launch_url,
            "Workspace": "Ready",
            "Elapsed": f"{self.metrics.restore_time:.1f} seconds"
        }
        self._record_evidence(f"Presentation Payload: {presentation_data}")
        
        self._emit_behavior_event("ResumeCompleted")
        
        return self._save_checkpoint()
        
    def _check_cancel_or_fail(self, result: dict, step: str) -> bool:
        if self._is_cancelled:
            return True
        if result.get("status") == "failed":
            self._emit_behavior_event("ResumeFailed")
            print(f"[{step} Failed] {result.get('error')}")
            return True
        return False

    def _handle_timeout(self, seconds: int):
        self._emit_behavior_event("ResumeTimeout")
        self._emit_behavior_event("RecoveryRequested", {"recovery": [{"action": "RETRY_VERIFICATION", "prompt": f"Server not ready after {seconds} seconds. Wait longer?"}]})
        print(f"[Timeout] Server not ready after {seconds} seconds. Offer: [Retry] [Logs] [Cancel]")

    def _record_evidence(self, message: str):
        print(f"[Evidence] {message}")

    def _stream_progress(self, message: str):
        # Emits timestamped events to Presentation Dashboard (CardLayout UI)
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] ✓ {message}")

    def _emit_behavior_event(self, event_type: str, payload: dict = None):
        # Triggers BehaviorEngine (Narration) rather than hardcoded TTS
        print(f"[EventBus] Emitting Behavior Event: {event_type} {payload if payload else ''}")

    def _save_checkpoint(self) -> ExecutionCheckpoint:
        return ExecutionCheckpoint(
            checkpoint_id=f"chk_{int(time.time())}",
            orchestrator_state=self.state.value,
            completed_steps=[],
            running_processes=[]
        )
