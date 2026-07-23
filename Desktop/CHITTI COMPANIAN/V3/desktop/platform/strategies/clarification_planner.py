import json
from desktop.models.interaction import InteractionEnvelope
from desktop.models.memory import MemorySnapshot
from desktop.models.cognition import PlanningDecision, PendingIntent
from desktop.brain.runtimes.planner_contracts import IPlannerStrategy
from desktop.app.inference_manager import InferenceManager
from desktop.app.prompt_builder import PromptBuilder
from desktop.models.inference import PromptContext, InferenceRequest
from desktop.app.context_selector import RuleBasedContextSelector
from desktop.app.context_budgeter import ContextBudgeter
from desktop.models.cognition import ContextSelectionPolicy, MemoryClass

class ClarificationPlannerStrategy(IPlannerStrategy):
    """
    Uses inference to generate exactly one targeted clarification question when the planner encounters ambiguity.
    Rule 194: Clarification Preserves Intent
    """
    def __init__(self, manager: InferenceManager, builder: PromptBuilder):
        self.manager = manager
        self.builder = builder
        self.context_selector = RuleBasedContextSelector(ContextSelectionPolicy([
            MemoryClass.WORKING_MEMORY,
            MemoryClass.RECENT_CONVERSATION,
            MemoryClass.FACT,
            MemoryClass.EPISODE,
            MemoryClass.SESSION_CONTEXT
        ]))
        
    async def plan(self, interaction: InteractionEnvelope, memory: MemorySnapshot) -> PlanningDecision:
        # 1. Select and budget context (same deterministic pipeline)
        selected = self.context_selector.select(interaction, memory)
        budgeter = ContextBudgeter(max_context=1000)
        
        system_rules = "You are CHITTI, a helpful assistant trying to clarify user intent."
        context = budgeter.budget_and_trim(
            selected=selected,
            policy=self.context_selector.policy,
            system_rules=system_rules,
            current_input=interaction.payload
        )
        
        # 2. Build clarification prompt
        prompt, _ = self.builder.build("Clarification", context)
        
        # 3. Generate response
        req = InferenceRequest(prompt=prompt, json_mode=True)
        resp = await self.manager.generate(req)
        
        try:
            data = json.loads(resp.raw_response)
            question = data.get("question", "Could you clarify your request?")
            missing_parameter = data.get("missing_parameter", "unknown")
            confidence = data.get("confidence", 1.0)
        except Exception:
            question = "Could you please provide more details?"
            missing_parameter = "unknown"
            confidence = 0.5
            
        # The intent must be preserved via PendingIntent before returning the decision
        # We will pass this data back to the HybridPlanner which can wrap it in a ClarificationWorkflow
        
        return PlanningDecision(
            workflow_name="ClarificationWorkflow",
            confidence=confidence,
            parameters={
                "question": question,
                "missing_parameter": missing_parameter
            },
            requires_approval=False
        )
