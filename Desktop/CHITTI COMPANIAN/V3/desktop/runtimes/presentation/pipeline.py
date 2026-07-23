import time
import logging
from typing import Dict, Any, List, Optional
from desktop.models.presentation import PresentationBundle, validate_presentation_bundle
from desktop.runtimes.presentation.contracts import PresentationSession, PresentationResult
from desktop.runtimes.presentation.registries import ExperienceRegistry, RendererRegistry

logger = logging.getLogger(__name__)

class BundleRouter:
    """
    S32E: Bundle routing stage validating PresentationBundle integrity and routing to ExperienceRegistry.
    """
    def __init__(self, experience_registry: ExperienceRegistry):
        self.experience_registry = experience_registry

    def route(self, bundle: PresentationBundle) -> Optional[Any]:
        if not validate_presentation_bundle(bundle):
            logger.warning("[BundleRouter] Invalid PresentationBundle rejected.")
            return None
        return self.experience_registry.get_experience(bundle.bundle_type, bundle.experience_type)

class PresentationSelector:
    """
    S32E: Experience selection stage resolving presentation experience fallback or exact match.
    """
    def select_experience(self, routed_experience: Optional[Any]) -> str:
        if routed_experience:
            if hasattr(routed_experience, "get_experience_name"):
                return routed_experience.get_experience_name()
            if hasattr(routed_experience, "__name__"):
                return routed_experience.__name__
            return str(routed_experience)
        return "DefaultPresentationExperience"

class AssetResolver:
    """
    S32E: Determines required renderers based on bundle metadata, experience, and SupportedRenderer list.
    """
    def resolve_renderers(self, bundle: PresentationBundle) -> List[str]:
        renderers = getattr(bundle, "supported_renderers", [])
        resolved = []
        for r in renderers:
            r_str = r.value if hasattr(r, "value") else str(r)
            resolved.append(r_str)
        return resolved if resolved else ["DASHBOARD_RENDERER"]

class PresentationComposer:
    """
    S32E: Composes PresentationSession context and prepares execution request.
    """
    def compose(self, bundle: PresentationBundle, experience_name: str, renderers: List[str]) -> PresentationSession:
        p_id = f"pres_{bundle.bundle_id}_{int(time.time() * 1000)}"
        session = PresentationSession(
            presentation_id=p_id,
            bundle_id=bundle.bundle_id,
            selected_experience=experience_name,
            selected_renderers=renderers,
            start_timestamp=time.time(),
            execution_status="RUNNING"
        )
        return session

from desktop.runtimes.presentation.framework import RendererOutput, RendererExecutionContext

class RendererDispatcher:
    """
    S32E/S32H: Universal Renderer Dispatcher invoking Renderer Lifecycle and producing RendererOutputCollection.
    """
    def __init__(self, renderer_registry: RendererRegistry):
        self.renderer_registry = renderer_registry

    def dispatch(self, session: PresentationSession, bundle: PresentationBundle) -> PresentationResult:
        start_t = time.time()
        output_list: List[RendererOutput] = []
        outputs_dict: Dict[str, Any] = {}
        statuses: Dict[str, str] = {}
        warnings: List[str] = []

        exec_context = RendererExecutionContext(
            presentation_id=session.presentation_id,
            bundle_id=bundle.bundle_id
        )

        for r_key in session.selected_renderers:
            r_start = time.time()
            renderer = self.renderer_registry.get_renderer(r_key)
            if renderer:
                try:
                    if hasattr(renderer, "initialize"):
                        renderer.initialize(exec_context)
                    if hasattr(renderer, "prepare"):
                        renderer.prepare(bundle)

                    if hasattr(renderer, "render"):
                        try:
                            res = renderer.render(bundle, exec_context)
                        except TypeError:
                            res = renderer.render(bundle)
                    elif callable(renderer):
                        res = renderer(bundle)
                    else:
                        res = f"Rendered by {renderer}"

                    if hasattr(renderer, "finalize"):
                        renderer.finalize()

                    r_dur = round((time.time() - r_start) * 1000.0, 2)

                    if isinstance(res, RendererOutput):
                        out_obj = res
                    else:
                        mime = "application/json" if isinstance(res, dict) else "text/plain"
                        out_obj = RendererOutput(
                            renderer_id=r_key,
                            renderer_type=r_key,
                            mime_type=mime,
                            payload=res,
                            execution_time_ms=r_dur
                        )

                    output_list.append(out_obj)
                    outputs_dict[r_key] = out_obj.payload
                    statuses[r_key] = "SUCCESS"
                except Exception as e:
                    logger.error(f"[RendererDispatcher] Error rendering '{r_key}': {e}")
                    statuses[r_key] = "FAILURE"
                    warnings.append(f"Renderer '{r_key}' failed: {e}")
            else:
                statuses[r_key] = "UNREGISTERED"
                outputs_dict[r_key] = f"No renderer registered for key '{r_key}'"
                warnings.append(f"Renderer '{r_key}' not registered in RendererRegistry.")

        elapsed_ms = round((time.time() - start_t) * 1000.0, 2)
        session.end_timestamp = time.time()
        overall_success = any(s == "SUCCESS" for s in statuses.values()) if statuses else False
        session.execution_status = "COMPLETED" if overall_success else "FAILED"

        return PresentationResult(
            presentation_id=session.presentation_id,
            bundle_id=bundle.bundle_id,
            success=overall_success,
            outputs=output_list,
            rendered_outputs=outputs_dict,
            renderer_status=statuses,
            execution_time_ms=elapsed_ms,
            warnings=warnings
        )
