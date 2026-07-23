from desktop.models.presentation import PresentationExperienceManifest

class ProductivityDashboardExperience:
    def get_manifest(self) -> PresentationExperienceManifest:
        return PresentationExperienceManifest(
            id="productivity_dashboard",
            name="Productivity Dashboard",
            version="1.0",
            layout="dashboard",
            recipe="DashboardRecipe",
            theme="productivity",
            skin="default"
        )
