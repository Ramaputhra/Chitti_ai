from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class NotifyUserCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Notifications")

class DismissNotificationCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Notifications")

class WatchNotificationCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Observation", supports_background=True, supports_cancel=True)
