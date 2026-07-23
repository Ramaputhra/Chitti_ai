import time
from typing import Dict, Any, List
from desktop.product.assistants.base import BaseAssistant, AssistantResponse, AutonomyLevel, Explanation, Evidence, AssistantContext, AssistantMetrics
from desktop.product.assistants.coding.models import DetectedGoal
from desktop.product.assistants.automation.models import (
    RiskLevel, AppStateNode, WorkflowConstraint, AutomationOutcome, AutomationPlan
)

class DesktopAutomationAssistant(BaseAssistant):
    """
    Solves the human job: "Automating goal-driven, multi-app workflows."
    Rule 153: Designs Intent, never mechanism.
    """
    def __init__(self, platform_max_risk: RiskLevel = RiskLevel.LOW):
        self.platform_max_risk = platform_max_risk

    async def process_intent(self, context: AssistantContext) -> AssistantResponse:
        metrics = AssistantMetrics()
        start_time = time.time()
        
        # 1. Observation & Context Recovery
        # e.g., Read user intent: "Send invoice to Accounting on Slack"
        user_intent = "Send invoice to Accounting on Slack"
        
        # 2. Environment Modeling
        slack_node = AppStateNode(
            application="Slack",
            state="Running in Background",
            focus="None",
            selection="None",
            dirty_state=False,
            permissions=["Read", "Write"],
            capabilities=["SendMessage", "UploadFile", "SwitchChannel"]
        )
        excel_node = AppStateNode(
            application="Excel",
            state="Invoice.xlsx Open",
            focus="Cell A1",
            selection="None",
            dirty_state=True,
            permissions=["Read", "Write"],
            capabilities=["Calculate", "Save", "ExportPDF"]
        )
        
        # 3. Constraint Analysis
        constraints = []
        if not excel_node.dirty_state:
            # We assume it's dirty here for demonstration
            pass
            
        # 4. Goal Detection
        goal = DetectedGoal(
            goal=user_intent,
            confidence=0.95,
            evidence=[{"source": "Slack", "status": "Running"}, {"source": "Excel", "status": "Open"}],
            alternatives={},
            missing_information=[]
        )
        
        # 5. Plan Preparation (Rule 153: Describe Intent, Never Mechanism)
        plan = AutomationPlan(
            goal=goal.goal,
            preconditions=["Invoice exists", "Slack authenticated", "Excel available"],
            intent_steps=["Extract invoice total from Excel", "Compose Slack message to #accounting", "Attach Invoice.xlsx", "Send Message"],
            postconditions=["Message delivered to #accounting"],
            constraints=constraints,
            outcome=AutomationOutcome(
                expected_state="Slack message sent",
                verification="Message exists in #accounting channel",
                rollback_possible=True,
                success_criteria="True"
            ),
            confidence=0.95,
            risk_level=RiskLevel.HIGH # Sending a message is a HIGH risk action
        )
        
        # 6. Suggestion & Rule 152 Enforcement
        # Rule 152: Risk Overrides Autonomy
        autonomy = AutonomyLevel.AUTONOMOUS # Assistant might *think* it can do this
        if plan.risk_level.value > self.platform_max_risk.value:
            autonomy = AutonomyLevel.EXECUTE_WITH_APPROVAL # Downgraded by platform policy
            
        explanation = Explanation(
            reason="I have mapped out the workflow to extract the invoice and send it to Slack.",
            evidence=[
                Evidence(
                    type="environment_model",
                    source="AppStateNode",
                    confidence=1.0,
                    payload={"Slack": slack_node.state, "Excel": excel_node.state}
                )
            ],
            confidence=plan.confidence,
            suggested_workflow={"action": "execute_automation_plan", "payload": plan.__dict__}
        )
        
        metrics.planning_time = (time.time() - start_time) * 1000
        
        return AssistantResponse(
            goal=goal.goal,
            autonomy=autonomy,
            explanation=explanation,
            metrics=metrics,
            payload={"plan": plan}
        )
