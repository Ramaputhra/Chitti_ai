from desktop.runtimes.capability.registry import CapabilityRegistry
from desktop.runtimes.capability.capabilities.identity.identity_capability import IdentityCapability
from desktop.runtimes.capability.descriptors import CapabilityDescriptor
from desktop.packages.desktop_pack.capabilities.expression import TextResponseCapability
from desktop.packages.desktop_pack.capabilities.execution import LaunchApplicationCapability, ExecuteTerminalCommandCapability

class CapabilityProvider:
    """
    Responsible for Dependency Injection of capabilities into the registry.
    (Dynamic Discovery deferred to future sprints)
    """
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def register_all(self):
        # Register IdentityCapability manually via DI
        identity_desc = IdentityCapability.get_descriptor()
        identity_desc.factory = lambda: IdentityCapability()
        self.registry.register(identity_desc)
        
        # Register TextResponseCapability for planner fallback
        text_desc = CapabilityDescriptor(
            id="TextResponseCapability",
            version="1.0",
            permissions=[],
            execution_mode="sync",
            category="Expression",
            action_name="text_response",
            description="Responds with text.",
            factory=lambda: TextResponseCapability()
        )
        self.registry.register(text_desc)
        
        # Register LaunchApplicationCapability
        launch_desc = CapabilityDescriptor(
            id="LaunchApplicationCapability",
            version="1.0",
            permissions=["desktop_control"],
            execution_mode="async",
            category="Execution",
            action_name="launch_application",
            description="Physically launches a standalone application.",
            factory=lambda: LaunchApplicationCapability()
        )
        self.registry.register(launch_desc)
        
        # Register ExecuteTerminalCommandCapability
        terminal_desc = CapabilityDescriptor(
            id="ExecuteTerminalCommandCapability",
            version="1.0",
            permissions=["desktop_control"],
            execution_mode="async",
            category="Execution",
            action_name="execute_terminal_command",
            description="Executes a terminal command attached to a working directory.",
            factory=lambda: ExecuteTerminalCommandCapability()
        )
        self.registry.register(terminal_desc)
