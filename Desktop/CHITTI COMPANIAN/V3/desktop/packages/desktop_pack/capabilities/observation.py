from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class ObserveDesktopCapability:
    """
    Subscribes to native OS events for reactive automation.
    Detects: active window changes, app launches, clipboard changes, etc.
    """
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Observation", supports_background=True, supports_cancel=True)
