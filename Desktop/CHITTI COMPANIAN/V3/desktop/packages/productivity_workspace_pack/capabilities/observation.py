from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class ObserveDocumentChangesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Observation", supports_background=True, supports_cancel=True)

class ObserveSpreadsheetUpdatesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Observation", supports_background=True, supports_cancel=True)

class ObservePresentationChangesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Observation", supports_background=True, supports_cancel=True)

class ObservePDFGenerationCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Observation", supports_background=True, supports_cancel=True)
