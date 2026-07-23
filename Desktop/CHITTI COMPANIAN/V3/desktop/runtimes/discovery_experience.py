class DiscoveryExperienceRuntime:
    """
    Observes the EventBus for newly registered plugins or capabilities
    and triggers the Experience Runtime to notify the user.
    """
    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        if self.event_bus:
            self.event_bus.subscribe("ServiceRegistered", self._on_service_registered)

    def _on_service_registered(self, payload: dict):
        """
        Example: "I noticed you've installed Photoshop support. I can now remove backgrounds."
        """
        service_id = payload.get("service_id")
        category = payload.get("category")
        
        # In a real implementation, we would route this to the ExperienceRuntime
        # to queue a proactive notification for the user.
        print(f"DiscoveryExperienceRuntime triggered: New {category} discovered: {service_id}")
