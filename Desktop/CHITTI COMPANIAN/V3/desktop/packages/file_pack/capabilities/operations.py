from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class CopyCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Operations", supports_pause=True, supports_resume=True)

class MoveCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Operations", supports_pause=True)

class DeleteCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Operations", requires_user_confirmation=True)

class CompressCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Operations", estimated_latency="high", supports_background=True)

class ExtractCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Operations", estimated_latency="high", supports_background=True)
