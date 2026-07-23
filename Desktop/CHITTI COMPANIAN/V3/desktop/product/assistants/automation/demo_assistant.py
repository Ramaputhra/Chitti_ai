import asyncio
from desktop.product.assistants.automation.assistant import DesktopAutomationAssistant
from desktop.product.assistants.automation.models import RiskLevel
from desktop.product.assistants.base import AssistantContext

async def verify_automation_assistant():
    print("--- Desktop Automation Assistant Verification (Sprint 65) ---\n")
    print("User Scenario: User asks 'Send the invoice to Accounting on Slack'.")
    print("Goal: Assistant models the environment, creates an AutomationPlan with Intent steps (Rule 153), and enforces Risk Overrides Autonomy (Rule 152).\n")
    
    # Platform policy is set to LOW risk allowed autonomously.
    assistant = DesktopAutomationAssistant(platform_max_risk=RiskLevel.LOW)
    context = AssistantContext(
        workspace=None, memory=None, timeline=None, user_goal=None, confidence=0.0,
        constraints=[], environment={}, planner_context={}
    )
    
    response = await assistant.process_intent(context)
    plan = response.payload['plan']
    
    print("=== Constraint Verification ===")
    
    # 1. Verify AutomationPlan Output
    print(f"1. Automation Plan Preconditions: {plan.preconditions}")
    print(f"   Automation Plan Postconditions: {plan.postconditions}")
    
    # 2. Verify Rule 153 (Intent, not mechanism)
    print(f"2. Rule 153 Intent Verification: {plan.intent_steps}")
    for step in plan.intent_steps:
        assert "Click" not in step # No mechanism allowed
        assert "Wait" not in step
        
    # 3. Verify Rule 152 (Risk Overrides Autonomy)
    print(f"3. Rule 152 Risk Override Verification:")
    print(f"   Plan Risk Level: {plan.risk_level.name}")
    print(f"   Platform Max Risk: {assistant.platform_max_risk.name}")
    print(f"   Final Autonomy Level: {response.autonomy.name}")
    assert response.autonomy.name == "EXECUTE_WITH_APPROVAL"
    
    print("\n✅ All structural constraints verified successfully!")
    print("The assistant behaves purely cognitively. It designs the intent safely and relies on the Planner and Task Orchestrator to execute it.")

if __name__ == "__main__":
    asyncio.run(verify_automation_assistant())
