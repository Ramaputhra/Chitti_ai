from desktop.models.environment import EnvironmentAction

class AdapterRouter:
    """
    Routes generic EnvironmentActions to the correct adapter instance.
    """
    def __init__(self, registry):
        self.registry = registry

    def route_action(self, action: EnvironmentAction):
        # find adapter, execute action payload
        print(f"[AdapterRouter] Routing action {action.action_type} to {action.target.adapter_id}")
