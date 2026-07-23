import uuid
from desktop.runtimes.execution.models import ExecutionPlan, ExecutionOperation

class OpenSettingsCapability:
    """
    Demonstrates Rule 110: A Capability only generates an ExecutionPlan, 
    it never executes the Win32/macOS APIs itself.
    """
    
    @property
    def name(self) -> str:
        return "open_settings"

    def build_plan(self) -> ExecutionPlan:
        plan_id = str(uuid.uuid4())
        
        # Action 1: Open the Start Menu/Search
        op1 = ExecutionOperation(
            provider_name="keyboard",
            action="shortcut",
            parameters={"keys": "Win+S"},
            expects=["Search Window Visible"]
        )
        
        # Action 2: Type "Settings"
        op2 = ExecutionOperation(
            provider_name="keyboard",
            action="type",
            parameters={"keys": "Settings"},
            requires=["Search Window Visible"]
        )
        
        # Action 3: Press Enter
        op3 = ExecutionOperation(
            provider_name="keyboard",
            action="press",
            parameters={"keys": "Enter"}
        )
        
        # Action 4: Wait and Verify
        op4 = ExecutionOperation(
            provider_name="window",
            action="focus",
            parameters={"title": "Settings"},
            expects=["Settings Window Active"],
            timeout_ms=10000
        )
        
        return ExecutionPlan(
            plan_id=plan_id,
            capability_name=self.name,
            operations=[op1, op2, op3, op4]
        )
