from desktop.packages.sdk.pack_metadata import CapabilityMetadata

class GitStatusCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Git")

class GitCommitCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Git", requires_user_confirmation=True)

class GitPullCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Git")

class GitPushCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Git", requires_user_confirmation=True)

class GitCheckoutBranchCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Git")
