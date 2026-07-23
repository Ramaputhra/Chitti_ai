from typing import List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor
from desktop.runtimes.presentation.models import PresentationModel, PresentationType, PresentationMetadata, PresentationCapability, PresentationLifetime
from desktop.runtimes.analytics.analytics_runtime import AnalyticsRuntime
from desktop.runtimes.analytics.models import AnalyticsQuery, TimeRange, Granularity

class AnalyticsCapability(ICapability):
    """Provides access to historical behavioral metrics and derived insights."""
    
    def __init__(self, analytics_runtime: AnalyticsRuntime):
        self.analytics_runtime = analytics_runtime
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "AnalyticsCapability"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> dict:
        return {"status": "healthy"}

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name="analytics",
            version="1.0",
            category="intelligence",
            permissions=[],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="get_analytics_report", 
                description="Get historical insights about the user's focus, context switches, and time allocation over a specific time range.", 
                parameters=[
                    {
                        "name": "time_range",
                        "type": "string",
                        "description": "The time range to query (e.g. today, week, month).",
                        "required": True
                    }
                ]
            )
        ]

    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name == "get_analytics_report"

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if not self.validate(invocation):
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Invalid tool."])
            
        time_range_str = invocation.parameters.get("time_range", "today").lower()
        time_range = TimeRange.TODAY
        if time_range_str == "week":
            time_range = TimeRange.WEEK
        elif time_range_str == "month":
            time_range = TimeRange.MONTH
            
        query = AnalyticsQuery(time_range=time_range, granularity=Granularity.DAY)
        report = self.analytics_runtime.run_query(query)
        
        # Transform AnalyticsReport into a PresentationModel
        presentation = PresentationModel(
            type=PresentationType.REPORT,
            title=f"Analytics Report: {time_range_str.capitalize()}",
            subtitle=f"Generated at {report.generated_at.strftime('%H:%M')}",
            icon="chart-bar",
            data={
                "focus_metrics": {
                    "total_focus_time_minutes": int(report.focus_metrics.total_focus_time_seconds / 60),
                    "deepest_context": report.focus_metrics.deepest_work_context or "N/A"
                },
                "insights": [i.description for i in report.insights],
                "top_applications": list(report.application_metrics.top_applications.keys())
            },
            actions=[],
            metadata=PresentationMetadata(
                capabilities=[PresentationCapability.SCROLL],
                lifetime=PresentationLifetime.TRANSIENT
            )
        )
        
        summary = f"Generated {time_range_str} analytics report. Deepest context was {report.focus_metrics.deepest_work_context}."
        
        return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=summary, presentation=presentation)

    def cancel(self, invocation_id: str) -> None:
        pass
