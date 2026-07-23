from desktop.packages.sdk.pack_metadata import CapabilityMetadata
from desktop.models.environment import EnvironmentContext

class OrganizeFolderCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Organization", requires_user_confirmation=True)

class RenameFilesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Organization")

class ArchiveFilesCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Organization")

class CleanupFolderCapability:
    def __init__(self):
        self.metadata = CapabilityMetadata(category="Organization", requires_user_confirmation=True)
