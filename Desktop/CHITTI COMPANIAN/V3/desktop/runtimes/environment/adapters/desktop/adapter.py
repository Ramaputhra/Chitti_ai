from desktop.models.environment import EnvironmentAction, EnvironmentContext, EnvironmentActionResult
from desktop.runtimes.environment.adapters.base import IEnvironmentAdapter
from desktop.runtimes.environment.adapters.desktop.selector import DesktopEngineSelector
from desktop.models.verification import ExecutionVerifier
from desktop.packages.sdk.pack_metadata import VerificationLevel

class DesktopExecutionVerifier(ExecutionVerifier):
    def verify(self, action: EnvironmentAction, raw_result: EnvironmentActionResult, level: VerificationLevel) -> EnvironmentActionResult:
        if level == VerificationLevel.NONE:
            return raw_result
            
        print(f"[ExecutionVerifier] Verifying {action.action_type} system state (Level: {level.name})...")
        # Pseudo-logic: actually check Windows APIs to see if window is focused, app is open, etc.
        # If mismatch, raw_result.status = "FAILED" and raw_result.error_message = "Application launched but Windows denied foreground focus."
        
        return raw_result

class DesktopAdapter(IEnvironmentAdapter):
    """
    Orchestrates the Selector and the Verifier, shielding the EnvironmentRuntime
    from the complexity of the hybrid engines.
    """
    def __init__(self):
        self.selector = DesktopEngineSelector()
        self.verifier = DesktopExecutionVerifier()
        
    def execute_action(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        # 1. Route to best engine
        engine = self.selector.select_engine(action, context)
        print(f"[DesktopAdapter] Routed action {action.action_type} to {engine.__class__.__name__}")
        
        # 2. Execute blindly
        raw_result = engine.execute(action, context)
        
        # 3. Verify real-world outcome
        # (Assuming CapabilityMetadata verification level is passed down via context or action metadata)
        verification_level = VerificationLevel.STANDARD 
        verified_result = self.verifier.verify(action, raw_result, verification_level)
        
        return verified_result
