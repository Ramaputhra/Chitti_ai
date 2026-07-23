from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class AnalyzeFolderCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Analysis", estimated_latency="high")

class CalculateFolderSizeCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Analysis")

class CompareFoldersCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Analysis", estimated_latency="high")
