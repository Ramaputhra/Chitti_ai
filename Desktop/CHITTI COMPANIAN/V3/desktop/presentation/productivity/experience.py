from typing import List
from desktop.models.presentation import BundleType, ExperienceType, SupportedRenderer
from desktop.runtimes.presentation.contracts import IPresentationExperience

class ProductivityDashboardExperience(IPresentationExperience):
    """
    S32F: Reference Productivity Dashboard Experience implementation.
    Consumes AnalyticsPresentationBundle and defines renderer composition requirements.
    Pure presentation composition; contains ZERO storage or business logic.
    """
    def get_experience_name(self) -> str:
        return "ProductivityDashboardExperience"

    def get_bundle_type(self) -> BundleType:
        return BundleType.ANALYTICS

    def get_experience_type( self ) -> ExperienceType:
        return ExperienceType.DASHBOARD

    def get_required_renderers(self) -> List[SupportedRenderer]:
        return [
            SupportedRenderer.DASHBOARD_RENDERER,
            SupportedRenderer.VOICE_RENDERER,
            SupportedRenderer.AVATAR_RENDERER
        ]
