from desktop.models.presentation import PresentationModel, PresentationExperienceContext, PresentationExperienceManifest
from desktop.platform.core.presentation.experience.recipe import IPresentationRecipe

class DashboardRecipe(IPresentationRecipe):
    def build_model(self, context: PresentationExperienceContext, manifest: PresentationExperienceManifest) -> PresentationModel:
        print(f"Building Dashboard Model for {manifest.id}")
        return PresentationModel()
        
    def validate(self, context: PresentationExperienceContext) -> bool: return True
    def supports(self, experience_id: str) -> bool: return True
    def estimate_cost(self) -> float: return 1.0

class SummaryRecipe(IPresentationRecipe):
    def build_model(self, context: PresentationExperienceContext, manifest: PresentationExperienceManifest) -> PresentationModel:
        print(f"Building Document Summary Model for {manifest.id}")
        return PresentationModel()
        
    def validate(self, context: PresentationExperienceContext) -> bool: return True
    def supports(self, experience_id: str) -> bool: return True
    def estimate_cost(self) -> float: return 1.5

class GalleryRecipe(IPresentationRecipe):
    def build_model(self, context: PresentationExperienceContext, manifest: PresentationExperienceManifest) -> PresentationModel:
        return PresentationModel()
    def validate(self, context: PresentationExperienceContext) -> bool: return True
    def supports(self, experience_id: str) -> bool: return True
    def estimate_cost(self) -> float: return 2.0

class WorkspaceRecipe(IPresentationRecipe):
    def build_model(self, context: PresentationExperienceContext, manifest: PresentationExperienceManifest) -> PresentationModel:
        return PresentationModel()
    def validate(self, context: PresentationExperienceContext) -> bool: return True
    def supports(self, experience_id: str) -> bool: return True
    def estimate_cost(self) -> float: return 2.5

class ComparisonRecipe(IPresentationRecipe):
    def build_model(self, context: PresentationExperienceContext, manifest: PresentationExperienceManifest) -> PresentationModel:
        return PresentationModel()
    def validate(self, context: PresentationExperienceContext) -> bool: return True
    def supports(self, experience_id: str) -> bool: return True
    def estimate_cost(self) -> float: return 3.0
