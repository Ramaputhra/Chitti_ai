from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class RestRequestCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="API", requires_network=True)

class WebhookListenerCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="API", requires_network=True, supports_background=True)

class WebhookTriggerCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="API", requires_network=True)

class WatchWebhookCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Observation", requires_network=True, supports_background=True, supports_cancel=True)
