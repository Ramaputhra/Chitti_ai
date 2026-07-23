from desktop.packages.file_pack.capabilities.discovery import SearchFilesCapability
from desktop.packages.file_pack.capabilities.organization import OrganizeFolderCapability
from desktop.models.environment import EnvironmentContext

class OrganizeFolderSkill:
    """
    General purpose organization skill. 
    Downloads, Desktop, Documents are just parameters to this skill.
    """
    def __init__(self):
        self.discover = SearchFilesCapability()
        self.organize = OrganizeFolderCapability()
        
    def execute(self, folder_path: str, context: EnvironmentContext):
        print(f"[OrganizeFolderSkill] Orchestrating cleanup for {folder_path}...")
        # 1. Discover logic
        # 2. Organize logic
        pass
