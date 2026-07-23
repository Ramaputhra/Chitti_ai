from desktop.models.capability import CapabilityResult, CapabilityAction
from desktop.app.capability_contracts import ICapability
from desktop.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus

class DistanceCapability(ICapability):
    """
    Sprint 134A: Hero Scenario Capability
    Determines distance between two locations and returns a generic CapabilityResult.
    """
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        origin = context.workflow.parameters.get("origin", "here")
        destination = context.workflow.parameters.get("destination", "Ameerpet")
        # Mock logic for the hero scenario to guarantee < 2s capability execution
        # In the future, this calls Google Maps API or similar.
        distance_km = 6.2
        duration_min = 18
        
        result = CapabilityResult(
            title=f"Distance to {destination}",
            summary=f"It is {distance_km} km away, approximately {duration_min} minutes by car.",
            spoken_response=f"The distance to {destination} is {distance_km} kilometers. It should take about {duration_min} minutes right now.",
            template_name="DistanceCard",
            template_data={
                "origin": origin,
                "destination": destination,
                "distance_km": distance_km,
                "duration_min": duration_min,
                "map_url": f"https://www.google.com/maps/dir/{origin}/{destination}".replace(" ", "+")
            },
            actions=[
                CapabilityAction(label="Open in Browser", action_id="OPEN_URL", metadata={"url": f"https://www.google.com/maps/dir/{origin}/{destination}".replace(" ", "+")})
            ]
        )
        return ExecutionResult(status=ExecutionStatus.SUCCESS, output_data={"capability_result": result})

def get_distance_capability_descriptor():
    from desktop.app.capability_contracts import CapabilityDescriptor
    return CapabilityDescriptor(
        id="DistanceCapability",
        version="1.0.0",
        permissions=["location", "web"],
        execution_mode="async",
        factory=DistanceCapability
    )
