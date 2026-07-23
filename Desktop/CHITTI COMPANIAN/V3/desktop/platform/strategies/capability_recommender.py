import json
from desktop.models.interaction import InteractionEnvelope
from desktop.models.memory import MemorySnapshot
from desktop.models.cognition import CapabilityRecommendation, CapabilitySuggestion, ContextSelectionPolicy, MemoryClass
from desktop.app.inference_manager import InferenceManager
from desktop.app.prompt_builder import PromptBuilder
from desktop.models.inference import InferenceRequest
from desktop.app.context_selector import RuleBasedContextSelector
from desktop.app.context_budgeter import ContextBudgeter

class LLMCapabilityRecommendationStrategy:
    """
    Suggests capabilities to fulfill an interaction. The output is ONLY a recommendation, 
    which the Planner must deterministically validate.
    Rule 196: Capability Recommendations Are Advisory
    """
    def __init__(self, manager: InferenceManager, builder: PromptBuilder):
        self.manager = manager
        self.builder = builder
        self.context_selector = RuleBasedContextSelector(ContextSelectionPolicy([
            MemoryClass.WORKING_MEMORY,
            MemoryClass.RECENT_CONVERSATION,
            MemoryClass.FACT
        ]))
        
    async def recommend(self, interaction: InteractionEnvelope, memory: MemorySnapshot, registry_manifest: str) -> CapabilityRecommendation:
        selected = self.context_selector.select(interaction, memory)
        budgeter = ContextBudgeter(max_context=2000)
        
        system_rules = f"You are CHITTI. Recommend capabilities from the following registry:\n{registry_manifest}"
        context = budgeter.budget_and_trim(
            selected=selected,
            policy=self.context_selector.policy,
            system_rules=system_rules,
            current_input=interaction.payload
        )
        
        prompt, _ = self.builder.build("RECOMMENDATION", context)
        
        req = InferenceRequest(prompt=prompt, json_mode=True)
        resp = await self.manager.generate(req)
        
        try:
            data = json.loads(resp.raw_response)
            suggestions = []
            for cap in data.get("candidate_capabilities", []):
                suggestions.append(CapabilitySuggestion(
                    capability_name=cap.get("capability_name", ""),
                    confidence=cap.get("confidence", 0.0),
                    parameters=cap.get("extracted_parameters", {}),
                    reason=cap.get("reason", "")
                ))
            
            return CapabilityRecommendation(
                candidate_capabilities=suggestions,
                confidence=data.get("confidence", 0.0),
                reasoning=data.get("reasoning", "")
            )
        except Exception as e:
            return CapabilityRecommendation(
                candidate_capabilities=[],
                confidence=0.0,
                reasoning=f"Failed to parse LLM response: {str(e)}"
            )
