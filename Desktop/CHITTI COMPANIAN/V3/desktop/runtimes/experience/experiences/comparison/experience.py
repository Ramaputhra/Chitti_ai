from desktop.models.presentation import PresentationExperienceManifest

class ComparisonReportExperience:
    def get_manifest(self) -> PresentationExperienceManifest:
        return PresentationExperienceManifest(
            id="comparison_report",
            name="Comparison Report",
            version="1.0",
            layout="split_view",
            recipe="ComparisonRecipe",
            theme="analytical",
            skin="default"
        )
