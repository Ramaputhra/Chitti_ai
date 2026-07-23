import asyncio
from desktop.models.cognition import CapabilityDescriptor, CapabilityRecommendation, CapabilitySuggestion, PlanningDecision
from desktop.brain.runtimes.planner_validation import CapabilityValidator

def test_capability_validation():
    registry = {
        "ReminderCapability": CapabilityDescriptor(
            name="ReminderCapability",
            description="Sets a reminder",
            parameter_schema=[{"name": "message", "required": True}, {"name": "time", "required": True}],
            permissions=[],
            execution_mode="sync"
        ),
        "EmailCapability": CapabilityDescriptor(
            name="EmailCapability",
            description="Sends an email",
            parameter_schema=[{"name": "recipient", "required": True}],
            permissions=[],
            execution_mode="sync"
        )
    }
    
    validator = CapabilityValidator(registry)
    
    # 1. Valid Recommendation
    rec1 = CapabilityRecommendation(
        candidate_capabilities=[
            CapabilitySuggestion("ReminderCapability", 0.9, {"message": "Call Mom", "time": "tomorrow"}, "")
        ],
        confidence=0.9,
        reasoning=""
    )
    decision1, missing1 = validator.validate(rec1)
    assert decision1 is not None
    assert decision1.workflow_name == "ReminderCapability"
    assert len(missing1) == 0
    
    # 2. Hallucinated Capability
    rec2 = CapabilityRecommendation(
        candidate_capabilities=[
            CapabilitySuggestion("MakeCoffeeCapability", 0.99, {}, "")
        ],
        confidence=0.99,
        reasoning=""
    )
    decision2, missing2 = validator.validate(rec2)
    assert decision2 is None
    
    # 3. Missing Required Parameter (routes to clarification)
    rec3 = CapabilityRecommendation(
        candidate_capabilities=[
            CapabilitySuggestion("ReminderCapability", 0.9, {"message": "Call Mom"}, "")
        ],
        confidence=0.9,
        reasoning=""
    )
    decision3, missing3 = validator.validate(rec3)
    assert decision3 is not None
    assert decision3.workflow_name == "ClarificationWorkflow"
    assert "time" in missing3
    
    print("✅ Capability Validation tests passed")

if __name__ == "__main__":
    print("--- Running Capability Recommendation Tests (Sprint 89) ---\n")
    test_capability_validation()
    print("\n✅ All Sprint 89 tests passed.")
