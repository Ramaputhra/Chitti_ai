from desktop.packages.sdk.pack_metadata import CapabilityMetadata, VerificationLevel

class CreateDocumentCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Documents", verification_level=VerificationLevel.STANDARD)

class ReadDocumentCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Documents")

class EditDocumentCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Documents", requires_user_confirmation=True, verification_level=VerificationLevel.STRICT)

class CompareDocumentsCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Documents")

class SummarizeDocumentCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Documents")

class ExportDocumentCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Documents", verification_level=VerificationLevel.STANDARD)
