from desktop.models.presentation import PresentationExperienceManifest

class GalleryViewerExperience:
    def get_manifest(self) -> PresentationExperienceManifest:
        return PresentationExperienceManifest(
            id="gallery_viewer",
            name="Media Gallery",
            version="1.0",
            layout="grid",
            recipe="GalleryRecipe",
            theme="dark",
            skin="glass"
        )
