from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class ReadClipboardCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Clipboard")

class WriteClipboardCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Clipboard", requires_user_confirmation=True)

class ClearClipboardCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Clipboard")
