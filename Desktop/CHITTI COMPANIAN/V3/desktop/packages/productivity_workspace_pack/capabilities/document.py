from desktop.packages.sdk.pack_metadata import CapabilityMetadata, VerificationLevel

class ResolveDocumentCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Document")

class VerifyDocumentCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Document", verification_level=VerificationLevel.STRICT)
        # Checks Exists, Hash, Renamed, Moved, Newer Version

class SmartDocumentRecoveryCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Document")
        # Cascades through Recent, Search Index, Recycle Bin, Cloud, Backups

class RestoreDocumentContextCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Document")
        # Restores scroll, highlights, zoom

class AnchorConversationCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Document")
        # Binds conversation context to document memory

class FetchRelatedKnowledgeCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Document")

class AskDocumentCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Document")
