import time
from typing import List, Dict, Any

from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor
from desktop.platform.shared.models.execution import ExecutionResult, ExecutionStatus

from desktop.platform.integrations.core.event_bus import EventBus
from desktop.capabilities.desktop.automation.runtime import DesktopAutomationRuntime

class DesktopAutomationCapability(ICapability):
    """
    Capability for physical desktop interactions & OS Control.
    Provides safe process control, application lifecycle management, and safety policies.
    """

    PROTECTED_PROCESSES = {
        "csrss.exe", "lsass.exe", "services.exe", "smss.exe", "winlogon.exe",
        "svchost.exe", "explorer.exe", "dwm.exe", "python.exe", "pythonw.exe", "chitti.exe"
    }

    ACTIVE_RENDER_APPS = {
        "premiere.exe", "adobe_premiere.exe", "blender.exe", "ffmpeg.exe"
    }

    def __init__(self, automation_runtime: DesktopAutomationRuntime, event_bus: EventBus):
        super().__init__()
        self.automation_runtime = automation_runtime
        self.event_bus = event_bus
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "DesktopAutomationCapability"

    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.automation_runtime.start_session()
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self.automation_runtime.end_session()
        self._state = ServiceState.STOPPED

    def health_check(self) -> dict:
        return {"status": "healthy"}

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name="desktop_automation",
            version="1.1",
            category="desktop",
            permissions=["keyboard", "mouse", "clipboard", "windows", "process_control"],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(name="launch", description="Launch an application.", parameters={"application": {"type": "string", "required": True}}),
            ToolDescriptor(name="type_text", description="Simulate typing text.", parameters={"text": {"type": "string", "required": True}}),
            ToolDescriptor(name="hotkey", description="Simulate a keyboard hotkey.", parameters={"keys": {"type": "array", "required": True}}),
            ToolDescriptor(name="mouse_click", description="Simulate a mouse click.", parameters={}),
            ToolDescriptor(name="wait", description="Wait for a duration.", parameters={"duration": {"type": "number", "required": True}}),
            ToolDescriptor(name="close_window", description="Close active window.", parameters={"window_title": {"type": "string", "required": False}}),
            ToolDescriptor(name="kill_process", description="Terminate a process.", parameters={"target": {"type": "string", "required": True}}),
            ToolDescriptor(name="suspend_process", description="Suspend a process.", parameters={"target": {"type": "string", "required": True}}),
            ToolDescriptor(name="resume_process", description="Resume a suspended process.", parameters={"target": {"type": "string", "required": True}}),
            ToolDescriptor(name="restart_process", description="Restart an application.", parameters={"application": {"type": "string", "required": True}}),
            ToolDescriptor(name="activate_window", description="Bring window to foreground.", parameters={"window_title": {"type": "string", "required": True}}),
            ToolDescriptor(name="open_folder", description="Open directory in File Explorer.", parameters={"folder_path": {"type": "string", "required": True}}),
            ToolDescriptor(name="open_file_location", description="Highlight file in File Explorer.", parameters={"filepath": {"type": "string", "required": True}})
        ]


    def _emit_telemetry(self, tool: str, params: dict, duration: float, status: str) -> None:
        if self.event_bus:
            from desktop.platform.shared.interfaces.event_bus import Event
            import uuid
            try:
                payload = {
                    "timestamp": time.time(),
                    "tool": tool,
                    "parameters": params,
                    "duration_ms": int(duration * 1000),
                    "status": status
                }
                evt = Event(event_id=str(uuid.uuid4()), source="DesktopAutomationCapability", payload=payload)
                self.event_bus.publish(evt)
            except Exception as e:
                print(f"[DesktopAutomationCapability] Telemetry publish warning: {e}")


    def execute(self, *args, **kwargs) -> ExecutionResult:
        if args and hasattr(args[0], "tool_name"):
            invocation = args[0]
            action = invocation.tool_name
            parameters = getattr(invocation, "parameters", getattr(invocation, "arguments", {}))
        else:
            action = kwargs.get("action")
            parameters = kwargs.get("parameters", {})
            
        start_time = time.time()
        try:
            result = self._handle_action(action, parameters)
            duration = time.time() - start_time
            is_success = (result.status == ExecutionStatus.SUCCESS)
            self._emit_telemetry(action, parameters, duration, "Success" if is_success else "Failed")
            return result
        except Exception as e:
            duration = time.time() - start_time
            self._emit_telemetry(action, parameters, duration, f"Failed: {str(e)}")
            return ExecutionResult(status=ExecutionStatus.FAILURE, summary=str(e), errors=[str(e)])

    def _handle_action(self, action: str, parameters: Dict[str, Any]) -> ExecutionResult:
        # Check Protected Process Safety Policy
        target = str(parameters.get("target", parameters.get("application", ""))).lower()
        if action in ["kill_process", "suspend_process"] and target in self.PROTECTED_PROCESSES:
            err = f"Security Exception: Modifying system or CHITTI process '{target}' is strictly prohibited."
            return ExecutionResult(
                status=ExecutionStatus.FAILURE,
                summary=err,
                errors=[err]
            )

        # Check Smart Execution Policy (Active Render Warning Interceptor)
        confirmed = parameters.get("confirmed", False)
        if action in ["kill_process", "restart_process"] and target in self.ACTIVE_RENDER_APPS and not confirmed:
            err = f"Smart Safety Gate: Process '{target}' is currently rendering video or 3D export. Confirmation required before termination."
            return ExecutionResult(
                status=ExecutionStatus.FAILURE,
                summary=err,
                data="CONFIRMATION_REQUIRED",
                errors=[err]
            )

        if action == "launch":
            app = parameters.get("application", "")
            out = self.automation_runtime.window_runtime.open(app)
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=out, data=out)
            
        elif action == "kill_process":
            out = self.automation_runtime.window_runtime.kill_process(target)
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=out, data=out)

        elif action == "suspend_process":
            out = self.automation_runtime.window_runtime.suspend_process(target)
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=out, data=out)

        elif action == "resume_process":
            out = self.automation_runtime.window_runtime.resume_process(target)
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=out, data=out)

        elif action == "restart_process":
            out = self.automation_runtime.window_runtime.restart_process(target)
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=out, data=out)

        elif action == "activate_window":
            title = parameters.get("window_title", "")
            self.automation_runtime.window_runtime.activate(title)
            out = f"Activated window {title}"
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=out, data=out)

        elif action == "open_folder":
            folder = parameters.get("folder_path", "")
            out = self.automation_runtime.window_runtime.open_folder(folder)
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=out, data=out)

        elif action == "open_file_location":
            filepath = parameters.get("filepath", "")
            out = self.automation_runtime.window_runtime.open_file_location(filepath)
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=out, data=out)

        elif action == "type_text":
            text = parameters.get("text", "")
            self.automation_runtime.input_driver.type_text(text)
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary="Typed text.", data="Typed text.")
            
        elif action == "hotkey":
            keys = parameters.get("keys", [])
            self.automation_runtime.input_driver.press_hotkey(*keys)
            out = f"Pressed hotkey: {keys}"
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=out, data=out)
            
        elif action == "mouse_click":
            self.automation_runtime.input_driver.click()
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary="Mouse clicked.", data="Mouse clicked.")
            
        elif action == "wait":
            duration = parameters.get("duration", 1)
            self.automation_runtime.wait(duration)
            out = f"Waited {duration} seconds."
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=out, data=out)
            
        elif action == "close_window":
            title = parameters.get("window_title")
            if title:
                self.automation_runtime.window_runtime.close(title)
            else:
                self.automation_runtime.input_driver.press_hotkey("alt", "f4")
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary="Closed window.", data="Closed window.")
            
        err = f"Unknown tool: {action}"
        return ExecutionResult(status=ExecutionStatus.FAILURE, summary=err, errors=[err])


