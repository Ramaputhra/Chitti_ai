from desktop.packages.sdk.pack_metadata import CapabilityMetadata, VerificationLevel

class CreatePresentationCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Presentation", verification_level=VerificationLevel.STANDARD)

class UpdatePresentationCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Presentation", requires_user_confirmation=True, verification_level=VerificationLevel.STRICT)

class ExportPresentationCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Presentation", verification_level=VerificationLevel.STANDARD)

class ReviewPresentationCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Presentation")
