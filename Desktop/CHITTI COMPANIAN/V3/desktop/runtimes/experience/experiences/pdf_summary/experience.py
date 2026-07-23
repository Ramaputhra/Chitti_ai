from desktop.models.presentation import PresentationExperienceManifest

class PDFSummaryExperience:
    def get_manifest(self) -> PresentationExperienceManifest:
        return PresentationExperienceManifest(
            id="pdf_summary",
            name="PDF Document Summary",
            version="1.0",
            layout="document",
            recipe="SummaryRecipe",
            theme="minimal",
            skin="default"
        )
