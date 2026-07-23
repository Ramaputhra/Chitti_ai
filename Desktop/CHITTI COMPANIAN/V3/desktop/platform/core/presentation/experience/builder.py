from desktop.models.presentation import (
    PresentationModel, 
    PresentationExperienceContext, 
    PresentationExperienceManifest,
    PresentationHistorySnapshot,
    ReplayMode
)
from desktop.platform.core.presentation.experience.recipe import IPresentationRecipe, RecipeValidator

class ExperienceBuilder:
    """
    Rule 341: Presentation Experiences define user-facing workflows. 
    The Experience Builder orchestrates the instantiation of an experience using a Recipe.
    """

    def build_experience(self, manifest: PresentationExperienceManifest, recipe: IPresentationRecipe, context: PresentationExperienceContext) -> PresentationModel:
        if not RecipeValidator.validate(manifest, recipe):
            raise ValueError(f"Recipe validation failed for experience {manifest.id}")
            
        if not recipe.validate(context):
            raise ValueError("Provided context is missing required datasets for this recipe.")

        return recipe.build_model(context, manifest)

    def replay_snapshot(self, snapshot: PresentationHistorySnapshot, mode: ReplayMode = ReplayMode.ORIGINAL) -> PresentationModel:
        """
        Rule 343: Experience replay restores immutable snapshots without re-executing workflows.
        """
        print(f"Replaying snapshot {snapshot.snapshot_id} in mode {mode.value}")
        return snapshot.presentation_model

    def compare_snapshots(self, snapshot_a: PresentationHistorySnapshot, snapshot_b: PresentationHistorySnapshot) -> PresentationModel:
        """
        Loads two snapshots and generates a comparison presentation model.
        """
        print(f"Comparing snapshot {snapshot_a.snapshot_id} with {snapshot_b.snapshot_id}")
        # In the future, this delegates to a 'ComparisonRecipe'
        return snapshot_b.presentation_model
