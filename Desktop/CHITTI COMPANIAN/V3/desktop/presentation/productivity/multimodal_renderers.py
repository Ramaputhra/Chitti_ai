import time
from typing import Dict, Any, List, Optional
from desktop.models.presentation import PresentationBundle, SupportedRenderer, AvatarState
from desktop.models.analytics import SuggestedNarrationFacts
from desktop.runtimes.presentation.contracts import IPresentationRenderer

class NarrationComposer:
    """
    S32G: Transforms SuggestedNarrationFacts into structured narration-ready content.
    Purely deterministic and factual. Contains ZERO LLM prompting or subjective opinions.
    """
    def compose_narration(self, facts: Optional[SuggestedNarrationFacts]) -> Dict[str, Any]:
        if not facts:
            return {
                "narration_text": "No productivity facts recorded for this session.",
                "facts_count": 0
            }
        
        app_name = facts.top_application or "Desktop"
        exec_count = facts.total_execution_count
        rate = facts.success_rate_percent
        
        narration_str = (
            f"Session summary: Primary application was {app_name}. "
            f"Total workflow executions recorded: {exec_count} with a {rate:.1f}% success rate."
        )
        
        return {
            "session_id": facts.session_id,
            "narration_text": narration_str,
            "top_application": app_name,
            "execution_count": exec_count,
            "success_rate_percent": rate,
            "facts_count": 3
        }

from desktop.runtimes.presentation.framework import (
    BaseRenderer, RendererOutput, RendererMetadata, RendererCapabilities
)

class VoiceRenderer(BaseRenderer, IPresentationRenderer):
    """
    S32G/S32H: Voice Renderer translating SuggestedNarrationFacts into RendererOutput.
    Contains ZERO direct database or runtime access.
    """
    def __init__(self):
        super().__init__()
        self.composer = NarrationComposer()

    def get_renderer_id(self) -> SupportedRenderer:
        return SupportedRenderer.VOICE_RENDERER

    def get_metadata(self) -> RendererMetadata:
        return RendererMetadata(
            renderer_name="VoiceRenderer",
            renderer_type="VOICE_RENDERER",
            supported_mime_types=["application/ssml+xml", "application/json"],
            supported_bundle_types=["ANALYTICS"]
        )

    def get_capabilities(self) -> RendererCapabilities:
        return RendererCapabilities(
            supports_audio=True,
            supports_streaming=True
        )

    def render(self, bundle: PresentationBundle, context: Optional[Any] = None) -> RendererOutput:
        start_t = time.time()
        facts = getattr(bundle, "suggested_narration_facts", None)
        composed = self.composer.compose_narration(facts)
        
        payload = {
            "renderer_type": "VOICE_RENDERER",
            "audio_format": "ssml",
            "speech_rate": 1.0,
            "narration": composed,
            "rendered_at": time.time()
        }
        dur = round((time.time() - start_t) * 1000.0, 2)
        return RendererOutput(
            renderer_id=SupportedRenderer.VOICE_RENDERER.value,
            renderer_type="VOICE_RENDERER",
            mime_type="application/ssml+xml",
            payload=payload,
            execution_time_ms=dur
        )

class AvatarExpressionMapper:
    """
    S32G: Structured rules mapping productivity facts to avatar expressions, gestures, and emphasis.
    Contains ZERO database, memory, or UI access.
    """
    def map_expression(self, bundle: PresentationBundle) -> Dict[str, Any]:
        metrics = getattr(bundle, "execution_metrics", None)
        facts = getattr(bundle, "suggested_narration_facts", None)

        success_rate = metrics.success_rate if metrics else 1.0
        exec_count = metrics.total_executions if metrics else 0
        replay_count = metrics.replay_count if metrics else 0

        # Expression mapping
        if success_rate >= 0.8:
            expression = "HAPPY"
            avatar_state = AvatarState.HAPPY.value
        elif success_rate < 0.5 and exec_count > 0:
            expression = "ATTENTIVE"
            avatar_state = AvatarState.THINKING.value
        else:
            expression = "NEUTRAL"
            avatar_state = AvatarState.IDLE.value

        # Gesture mapping
        gesture = "NOD" if exec_count > 0 else "IDLE"
        emphasis = "HIGH" if replay_count > 0 else "NORMAL"

        return {
            "expression": expression,
            "avatar_state": avatar_state,
            "gesture": gesture,
            "emphasis_level": emphasis
        }

class AvatarRenderer(BaseRenderer, IPresentationRenderer):
    """
    S32G/S32H: Avatar Renderer mapping AnalyticsPresentationBundle facts to RendererOutput.
    Contains ZERO UI code or narration text.
    """
    def __init__(self):
        super().__init__()
        self.mapper = AvatarExpressionMapper()

    def get_renderer_id(self) -> SupportedRenderer:
        return SupportedRenderer.AVATAR_RENDERER

    def get_metadata(self) -> RendererMetadata:
        return RendererMetadata(
            renderer_name="AvatarRenderer",
            renderer_type="AVATAR_RENDERER",
            supported_mime_types=["application/json"],
            supported_bundle_types=["ANALYTICS"]
        )

    def get_capabilities(self) -> RendererCapabilities:
        return RendererCapabilities(
            supports_animation=True
        )

    def render(self, bundle: PresentationBundle, context: Optional[Any] = None) -> RendererOutput:
        start_t = time.time()
        mapping = self.mapper.map_expression(bundle)
        session_id = getattr(bundle, "session_id", "global")
        
        payload = {
            "renderer_type": "AVATAR_RENDERER",
            "session_id": session_id,
            "expression": mapping["expression"],
            "avatar_state": mapping["avatar_state"],
            "gesture": mapping["gesture"],
            "emphasis_level": mapping["emphasis_level"],
            "animation_trigger": f"trigger_avatar_{mapping['expression'].lower()}",
            "rendered_at": time.time()
        }
        dur = round((time.time() - start_t) * 1000.0, 2)
        return RendererOutput(
            renderer_id=SupportedRenderer.AVATAR_RENDERER.value,
            renderer_type="AVATAR_RENDERER",
            mime_type="application/json",
            payload=payload,
            execution_time_ms=dur
        )
