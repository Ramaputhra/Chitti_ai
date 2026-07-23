from typing import List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor
from desktop.runtimes.presentation.models import PresentationModel, PresentationType, PresentationMetadata, PresentationCapability, PresentationLifetime
from desktop.runtimes.prediction.prediction_runtime import PredictionRuntime
from desktop.runtimes.prediction.models import ForecastType, ForecastPriority

class PredictionCapability(ICapability):
    """Provides access to the user's predicted behavioral trajectories."""
    
    def __init__(self, prediction_runtime: PredictionRuntime):
        self.prediction_runtime = prediction_runtime
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "PredictionCapability"

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
            name="prediction",
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
                name="get_active_forecasts", 
                description="Get hypotheses about the user's immediate future routines, risks, and opportunities.", 
                parameters=[]
            )
        ]

    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name == "get_active_forecasts"

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if not self.validate(invocation):
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Invalid tool."])
            
        prediction_state = self.prediction_runtime.get_current_forecast()
        
        forecast_items = []
        for f in prediction_state.active_forecasts:
            forecast_items.append({
                "type": f.type.value.upper(),
                "hypothesis": f.hypothesis,
                "confidence": f"{int(f.confidence * 100)}%",
                "priority": f.priority.value.upper(),
                "horizon": f.horizon.value.upper(),
                "severity": f.severity.value.upper() if f.severity else "NONE"
            })
            
        presentation = PresentationModel(
            type=PresentationType.LIST,
            title="Behavioral Forecast",
            subtitle="Active Predictions",
            icon="crystal-ball",
            data={
                "items": forecast_items
            },
            actions=[],
            metadata=PresentationMetadata(
                capabilities=[PresentationCapability.SCROLL],
                lifetime=PresentationLifetime.TRANSIENT
            )
        )
        
        summary = f"Generated {len(prediction_state.active_forecasts)} active behavior forecasts."
        
        return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=summary, presentation=presentation)

    def cancel(self, invocation_id: str) -> None:
        pass
