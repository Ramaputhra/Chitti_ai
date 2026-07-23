from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class KeyboardInputCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Input", requires_user_confirmation=True)

class MouseInputCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Input", requires_user_confirmation=True)

class ScrollCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Input")

class DragDropCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Input", requires_user_confirmation=True)

class HotkeyCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Input")
