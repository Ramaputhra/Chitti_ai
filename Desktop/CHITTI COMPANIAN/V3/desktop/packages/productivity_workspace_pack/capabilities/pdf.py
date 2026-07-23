from desktop.packages.sdk.pack_metadata import CapabilityMetadata, VerificationLevel

class ReadPDFCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="PDF")

class MergePDFCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="PDF", verification_level=VerificationLevel.STANDARD)

class SplitPDFCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="PDF", verification_level=VerificationLevel.STANDARD)

class ExtractPDFCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="PDF")

class SignPDFCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="PDF", requires_user_confirmation=True, verification_level=VerificationLevel.STRICT)

class ExportPDFCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="PDF", verification_level=VerificationLevel.STANDARD)
