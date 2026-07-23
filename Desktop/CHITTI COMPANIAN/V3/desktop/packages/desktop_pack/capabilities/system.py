from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class GetFocusedApplicationCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="System")

class ListRunningApplicationsCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="System")

class LaunchApplicationCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="System")

class TerminateApplicationCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="System", requires_user_confirmation=True)
