from typing import List, Dict, Any
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.platform.shared.models.execution import ExecutionResult
from desktop.runtimes.capability.base import BaseCapability
from desktop.capabilities.system.operations_runtime import SystemOperationsRuntime, OperationPlan, PrivilegeContext
import time

class SystemOperationsCapability(BaseCapability):
    """
    Capability for executing privileged OS-level operations.
    Acts entirely through the SystemOperationsRuntime and requires an immutable OperationPlan.
    """
    def __init__(self, runtime: SystemOperationsRuntime):
        super().__init__()
        self.runtime = runtime
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "SystemOperationsCapability"

    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> dict:
        return {"status": "healthy"}

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name="system_operations",
            version="1.0",
            category="system",
            permissions=["system.install", "system.uninstall"],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="install",
                description="Install software based on an immutable OperationPlan.",
                parameters=[
                    ToolParameter(name="package", type="string", description="The package name.", required=True),
                    ToolParameter(name="method", type="string", description="The installer method (e.g. winget, msi).", required=True),
                    ToolParameter(name="source", type="string", description="Optional source URL or path.", required=False)
                ]
            ),
            ToolDescriptor(
                name="uninstall",
                description="Uninstall software based on an immutable OperationPlan.",
                parameters=[
                    ToolParameter(name="package", type="string", description="The package name.", required=True),
                    ToolParameter(name="method", type="string", description="The installer method.", required=True)
                ]
            ),
            ToolDescriptor(
                name="verify_installation",
                description="Verify if software is installed using a specified strategy.",
                parameters=[
                    ToolParameter(name="package", type="string", description="The package name.", required=True),
                    ToolParameter(name="strategy", type="string", description="The verification strategy.", required=True)
                ]
            )
        ]

    def execute(self, *args, **kwargs) -> ExecutionResult:
        action = kwargs.get("action")
        parameters = kwargs.get("parameters", {})
        
        if args and hasattr(args[0], "tool_name"):
            action = args[0].tool_name
            parameters = args[0].parameters

        if action == "verify_installation":
            package = parameters.get("package")
            strategy = parameters.get("strategy")
            success = self.runtime.verify(package, strategy)
            return ExecutionResult(success=success, output=f"Verification {'succeeded' if success else 'failed'}")

        # Construct plan (mocking PrivilegeContext as it would be injected by orchestration)
        plan = OperationPlan(
            operation=action,
            package=parameters.get("package"),
            source=parameters.get("source"),
            method=parameters.get("method")
        )
        
        ctx = PrivilegeContext(
            requires_admin=True,
            approval_id="mock_approval",
            approved_by="User",
            approved_at=time.time(),
            operation_hash="12345"
        )
        
        try:
            success = self.runtime.execute_plan(plan, ctx)
            return ExecutionResult(success=success, output=f"Successfully executed {action} for {plan.package}")
        except Exception as e:
            return ExecutionResult(success=False, error=str(e))
