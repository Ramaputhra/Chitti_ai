import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from desktop.models.presentation import PresentationBundle, SupportedRenderer
from desktop.models.analytics import (
    AnalyticsPresentationBundle, ActivityTimeline, ExecutionMetrics,
    ProductivitySummary, InsightCard
)
from desktop.runtimes.presentation.contracts import IPresentationRenderer

class TimelineRenderer:
    """
    S32F: Renders ActivityTimeline into structured chronological activity representation.
    Contains ZERO database access or LLM logic.
    """
    def render_timeline(self, timeline: Optional[ActivityTimeline]) -> List[Dict[str, Any]]:
        if not timeline or not timeline.entries:
            return []
        rendered = []
        for entry in timeline.entries:
            rendered.append({
                "entry_id": entry.entry_id,
                "timestamp": entry.timestamp,
                "event_type": entry.event_type,
                "app_identity": entry.app_identity,
                "window_title": entry.window_title,
                "duration_ms": entry.duration_ms
            })
        return rendered

class StatisticsRenderer:
    """
    S32F: Renders ExecutionMetrics into structured execution statistics representation.
    Contains ZERO database access or LLM logic.
    """
    def render_statistics(self, metrics: Optional[ExecutionMetrics]) -> Dict[str, Any]:
        if not metrics:
            return {}
        return {
            "total_executions": metrics.total_executions,
            "success_count": metrics.success_count,
            "failure_count": metrics.failure_count,
            "success_rate_percent": round(metrics.success_rate * 100.0, 2),
            "avg_duration_ms": metrics.avg_duration_ms,
            "replay_count": metrics.replay_count
        }

class InsightCardRenderer:
    """
    S32F: Renders InsightCards into structured factual insight card representations.
    Contains ZERO database access or LLM logic.
    """
    def render_insight_cards(self, cards: List[InsightCard]) -> List[Dict[str, Any]]:
        rendered = []
        for card in cards:
            rendered.append({
                "card_id": card.card_id,
                "metric_key": card.metric_key,
                "metric_value": card.metric_value,
                "category": card.category,
                "timestamp": card.timestamp
            })
        return rendered

from desktop.runtimes.presentation.framework import (
    BaseRenderer, RendererOutput, RendererMetadata, RendererCapabilities
)

class DashboardRenderer(BaseRenderer, IPresentationRenderer):
    """
    S32F/S32H: Master composite Productivity Dashboard Renderer adhering to Renderer Framework.
    Combines Summary, Timeline, Statistics, and Insight Cards sections into a clean Presentation Layout structure.
    Receives ONLY data contained inside AnalyticsPresentationBundle.
    """
    def __init__(self):
        super().__init__()
        self.timeline_renderer = TimelineRenderer()
        self.statistics_renderer = StatisticsRenderer()
        self.insight_renderer = InsightCardRenderer()

    def get_renderer_id(self) -> SupportedRenderer:
        return SupportedRenderer.DASHBOARD_RENDERER

    def get_metadata(self) -> RendererMetadata:
        return RendererMetadata(
            renderer_name="DashboardRenderer",
            renderer_type="DASHBOARD_RENDERER",
            supported_mime_types=["application/json"],
            supported_bundle_types=["ANALYTICS"]
        )

    def get_capabilities(self) -> RendererCapabilities:
        return RendererCapabilities(
            supports_animation=False,
            supports_audio=False,
            supports_interaction=True
        )

    def render(self, bundle: PresentationBundle, context: Optional[Any] = None) -> RendererOutput:
        start_t = time.time()
        session_id = getattr(bundle, "session_id", "global")
        summary_obj = getattr(bundle, "productivity_summary", None)
        metrics_obj = getattr(bundle, "execution_metrics", None)
        timeline_obj = getattr(bundle, "activity_timeline", None)
        insights_obj = getattr(bundle, "insight_cards", [])

        summary_data = summary_obj.__dict__ if summary_obj else {}
        timeline_data = self.timeline_renderer.render_timeline(timeline_obj)
        stats_data = self.statistics_renderer.render_statistics(metrics_obj)
        insights_data = self.insight_renderer.render_insight_cards(insights_obj)

        activity_dist = {}
        if timeline_obj and timeline_obj.entries:
            for e in timeline_obj.entries:
                app = e.app_identity
                activity_dist[app] = activity_dist.get(app, 0) + 1

        layout = {
            "layout_title": f"Today's Productivity Dashboard — Session [{session_id}]",
            "sections": {
                "summary": summary_data,
                "timeline": timeline_data,
                "execution_statistics": stats_data,
                "insight_cards": insights_data,
                "activity_distribution": activity_dist
            },
            "rendered_at": time.time()
        }

        dur = round((time.time() - start_t) * 1000.0, 2)
        return RendererOutput(
            renderer_id=SupportedRenderer.DASHBOARD_RENDERER.value,
            renderer_type="DASHBOARD_RENDERER",
            mime_type="application/json",
            payload=layout,
            execution_time_ms=dur
        )
