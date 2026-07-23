from desktop.models.presentation import PresentationExperienceManifest

class DeveloperWorkspaceExperience:
    def get_manifest(self) -> PresentationExperienceManifest:
        return PresentationExperienceManifest(
            id="developer_workspace",
            name="Platform Diagnostics",
            version="1.0",
            layout="workspace",
            recipe="WorkspaceRecipe",
            theme="developer",
            skin="terminal"
        )
