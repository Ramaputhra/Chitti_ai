from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class ReadEmailCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Email")

class SearchEmailCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Email")

class ComposeEmailCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Email")

class SendEmailCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Email", requires_user_confirmation=True)

class ReplyEmailCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Email", requires_user_confirmation=True)

class ForwardEmailCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Email", requires_user_confirmation=True)

class WatchInboxCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Observation", supports_background=True, supports_cancel=True)
