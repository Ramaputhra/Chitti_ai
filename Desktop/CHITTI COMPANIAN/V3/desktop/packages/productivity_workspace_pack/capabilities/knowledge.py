from desktop.packages.sdk.pack_metadata import CapabilityMetadata, VerificationLevel

class CaptureNotesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Knowledge", verification_level=VerificationLevel.STANDARD)

class OrganizeNotesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Knowledge", verification_level=VerificationLevel.STRICT)

class SearchNotesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Knowledge")
