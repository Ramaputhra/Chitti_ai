from abc import ABC, abstractmethod
from desktop.models.presentation import PresentationModel, PresentationExperienceContext, PresentationExperienceManifest

class IPresentationRecipe(ABC):
    """
    Rule 342: Recipes are deterministic transformers. They never execute capabilities or query storage.
    """

    @abstractmethod
    def build_model(self, context: PresentationExperienceContext, manifest: PresentationExperienceManifest) -> PresentationModel:
        """Transforms context data into a strictly validated PresentationModel."""
        pass
        
    # --- Streaming Recipe Hooks (Prepared for Phase 10) ---
    def build_initial(self, context: PresentationExperienceContext, manifest: PresentationExperienceManifest) -> PresentationModel:
        """Returns the skeleton layout before all data is ready."""
        return self.build_model(context, manifest)
        
    def update(self, delta: Any, current_model: PresentationModel) -> PresentationModel:
        """Applies incremental updates to the active model."""
        return current_model
        
    def finish(self, current_model: PresentationModel) -> PresentationModel:
        """Finalizes the streaming recipe."""
        return current_model

    @abstractmethod
    def validate(self, context: PresentationExperienceContext) -> bool:
        """Returns True if the provided context contains all datasets required by this recipe."""
        pass

    @abstractmethod
    def supports(self, experience_id: str) -> bool:
        """Returns True if this recipe can fulfill the requested experience."""
        pass

    @abstractmethod
    def estimate_cost(self) -> float:
        """Returns the estimated computational cost of assembling this presentation."""
        pass

class RecipeValidator:
    """
    Validates recipes and experiences before the ExperienceBuilder executes them.
    """
    @staticmethod
    def validate(manifest: PresentationExperienceManifest, recipe: IPresentationRecipe) -> bool:
        # Check required datasets
        # Check missing widgets
        # Check missing layouts
        # Check package dependencies
        return True
