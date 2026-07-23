import logging
from typing import List, Optional, Any, Dict
from desktop.models.lifecycle import IRuntime, HealthState
from desktop.models.presentation import PresentationBundle, validate_presentation_bundle
from desktop.runtimes.presentation.contracts import PresentationSession, PresentationResult
from desktop.runtimes.presentation.registries import ExperienceRegistry, RendererRegistry
from desktop.runtimes.presentation.pipeline import (
    BundleRouter, PresentationSelector, AssetResolver, PresentationComposer, RendererDispatcher
)

logger = logging.getLogger(__name__)

class PresentationRuntime(IRuntime):
    """
    S32E: Presentation Runtime — Universal Experience Platform.
    Responsible for validating, routing, composing, and dispatching any PresentationBundle derivative.
    Domain-agnostic, renderer-agnostic, and UI-agnostic.
    Contains ZERO direct database access.
    """
    def __init__(self):
        self._running = False
        self._context = None
        
        # Subsystems & Registries
        self.experience_registry = ExperienceRegistry()
        self.renderer_registry = RendererRegistry()
        self.bundle_router = BundleRouter(self.experience_registry)
        self.selector = PresentationSelector()
        self.asset_resolver = AssetResolver()
        self.composer = PresentationComposer()
        self.dispatcher = RendererDispatcher(self.renderer_registry)

    @property
    def dependencies(self):
        return []

    def health(self) -> HealthState:
        return HealthState.HEALTHY if self._running else HealthState.DEGRADED

    async def initialize(self, context: Any = None) -> bool:
        self._context = context
        logger.info("[PresentationRuntime] Initialized universal experience platform.")
        return True

    async def start(self) -> bool:
        self._running = True
        logger.info("[PresentationRuntime] Started presentation runtime.")
        return True

    async def stop(self) -> bool:
        self._running = False
        logger.info("[PresentationRuntime] Stopped presentation runtime.")
        return True

    async def shutdown(self) -> bool:
        await self.stop()
        return True

    def register_experience(self, bundle_type: Any, experience_type: Any, experience: Any):
        """
        Public API: Register a domain presentation experience with ExperienceRegistry.
        """
        self.experience_registry.register_experience(bundle_type, experience_type, experience)

    def register_renderer(self, renderer_key: Any, renderer: Any):
        """
        Public API: Register a presentation renderer with RendererRegistry.
        """
        self.renderer_registry.register_renderer(renderer_key, renderer)

    def render_bundle(self, bundle: PresentationBundle) -> PresentationResult:
        """
        Public API: Executes universal PresentationRuntime pipeline for any PresentationBundle derivative.
        Pipeline: PresentationBundle -> BundleRouter -> ExperienceRegistry -> PresentationSelector -> AssetResolver -> PresentationComposer -> RendererDispatcher -> PresentationResult
        """
        if not validate_presentation_bundle(bundle):
            logger.error("[PresentationRuntime] Render attempt rejected: Invalid PresentationBundle.")
            return PresentationResult(
                presentation_id="invalid",
                bundle_id=getattr(bundle, "bundle_id", "unknown"),
                success=False,
                warnings=["Invalid PresentationBundle rejected by validate_presentation_bundle."]
            )

        routed_exp = self.bundle_router.route(bundle)
        exp_name = self.selector.select_experience(routed_exp)
        required_renderers = self.asset_resolver.resolve_renderers(bundle)
        session = self.composer.compose(bundle, exp_name, required_renderers)
        result = self.dispatcher.dispatch(session, bundle)

        logger.info(f"[PresentationRuntime] Render complete for bundle '{bundle.bundle_id}' (Success: {result.success}).")
        return result
