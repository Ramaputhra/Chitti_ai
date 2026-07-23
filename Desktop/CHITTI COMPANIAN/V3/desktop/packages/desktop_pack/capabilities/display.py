from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class GetDisplaysCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Display")

class SetPrimaryDisplayCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Display")

class SwitchDisplayCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Display")

class GetResolutionCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Display")
