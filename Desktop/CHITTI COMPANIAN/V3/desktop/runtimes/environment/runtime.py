from desktop.runtimes.environment.manager import EnvironmentManager
from desktop.runtimes.environment.registry import AdapterRegistry
from desktop.runtimes.environment.router import AdapterRouter
from desktop.runtimes.environment.session_manager import EnvironmentSessionManager
from desktop.runtimes.environment.resource_coordinator import ResourceCoordinator
from desktop.runtimes.environment.telemetry import EnvironmentTelemetry

class EnvironmentRuntime:
    """
    The main facade for the Environment Interaction Platform.
    Capabilities invoke the Runtime, NEVER the adapters directly.
    """
    def __init__(self):
        self.manager = EnvironmentManager()
        self.registry = AdapterRegistry()
        self.router = AdapterRouter(self.registry)
        self.session_manager = EnvironmentSessionManager()
        self.resource_coordinator = ResourceCoordinator()
        self.telemetry = EnvironmentTelemetry()

    def execute(self, action):
        self.router.route_action(action)
