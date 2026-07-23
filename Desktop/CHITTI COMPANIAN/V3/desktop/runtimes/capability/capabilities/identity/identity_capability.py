import sys
import platform
from desktop.runtimes.capability.descriptors import CapabilityDescriptor, VerificationSupport
from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
from desktop.runtimes.capability.context import CapabilityContext
from desktop.app.capability_contracts import CapabilityExecutionMode


class IdentityCapability:
    """
    Provides information about CHITTI's identity, version, and platform.
    Adheres to the stateless, side-effect-free capability rules.
    """
    
    @staticmethod
    def get_descriptor() -> CapabilityDescriptor:
        return CapabilityDescriptor(
            id="core.identity",
            version="1.0.0",
            permissions=[],
            execution_mode=CapabilityExecutionMode.SYNC,
            category="System",
            action_name="get_identity",
            description="Get the AI's identity, core purpose, software version, and platform information.",
            examples=["Who are you?", "What is your version?", "What OS are we running on?"],
            parameters_schema={},
            factory=lambda: IdentityCapability()
        )

    def execute(self, context: CapabilityContext) -> ExecutionResult:
        if context.logger:
            context.logger.info("Executing IdentityCapability...")
            
        info = {
            "identity": "I am CHITTI, a desktop AI companion operating on Platform v3.0.",
            "version": "Platform Version 3.0 (Sprint 15 Hardening)",
            "os": f"{platform.system()} {platform.release()} ({platform.architecture()[0]})",
            "python": sys.version
        }
        
        # Format the output in a way that the TextResponseCapability or similar downstream component can present.
        # Returning it as a formatted string in a primary 'text' output for now to maintain compatibility with
        # any downstream renderer that just wants a string.
        formatted_text = "\n".join([f"{k.capitalize()}: {v}" for k, v in info.items()])
        info["text"] = formatted_text
        
        return ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            outputs=info
        )
