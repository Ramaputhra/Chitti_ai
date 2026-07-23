from desktop.packages.file_pack.models.public.semantic import DirectoryListing
from desktop.models.presentation import PresentationModel, Widget, TextWidget

class WorkspaceExperience:
    """
    Semantic presentation. Can display folders, projects, archives, or cloud storage without changing layout.
    """
    def present(self, listing: DirectoryListing):
        print(f"[WorkspaceExperience] Rendering Workspace for {listing.directory_path}")
        # Build widgets from the dataset
        pass
