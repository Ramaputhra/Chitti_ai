from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class ExecuteCommandCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Terminal", requires_user_confirmation=True)

class StopCommandCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Terminal")
