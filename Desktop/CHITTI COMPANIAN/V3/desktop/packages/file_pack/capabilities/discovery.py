from desktop.packages.sdk.pack_metadata import CapabilityMetadata
from desktop.models.environment import EnvironmentContext

class SearchFilesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Discovery", offline_capable=True)

class FindDuplicatesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Discovery", estimated_latency="high", offline_capable=True)

class FindLargeFilesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Discovery", offline_capable=True)

class FindRecentFilesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Discovery", offline_capable=True)
