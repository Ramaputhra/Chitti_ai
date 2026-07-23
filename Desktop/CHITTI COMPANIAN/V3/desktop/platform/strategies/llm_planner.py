from uuid import uuid4
from desktop.app.planner_contracts import IPlannerStrategy
from desktop.models.interaction import InteractionEnvelope
from desktop.models.memory import MemorySnapshot
from desktop.models.cognition import PlanningDecision, ExecutionPlan, WorkflowRequest, ExecutionPolicy, RetryPolicy, ConfidencePolicy, ApprovalRequirement
from desktop.models.cognition import Intent, GreetingIntent, SystemIntent
from desktop.app.inference_contracts import IInferenceStrategy

# A quick shim for new intents until we fully define them
class GenericIntent(Intent):
    def __init__(self, name: str, confidence: float, entities: dict):
        super().__init__(name, confidence)
        self.entities = entities

class LLMPlannerStrategy(IPlannerStrategy):
    """
    Uses an Inference Strategy to classify intent, then deterministically maps it to workflows.
    (Rule 184: Inference is advisory. The Planner owns the ExecutionPlan).
    """
    def __init__(self, inference_strategy: IInferenceStrategy, confidence_policy: ConfidencePolicy = None):
        self.inference = inference_strategy
        self.policy = confidence_policy or ConfidencePolicy.STRICT

    def parse_intent(self, interaction, context):
        pass

    def formulate_decision(self, intent, context):
        pass

    async def plan(self, interaction: InteractionEnvelope, memory: MemorySnapshot) -> PlanningDecision:
        # COG-31B: Memory-Aware LLM Planning
        # Consumes ONLY MemoryEpisodeHint objects projected in memory.episode_hints.
        # Formatted exclusively via PromptBuilder (Rule 38/41).
        hints = getattr(memory, "episode_hints", []) or []
        experience_context = ""
        planning_mode = "zero_shot"

        if hints:
            from desktop.app.prompt_builder import PromptBuilder
            experience_context = PromptBuilder.format_experience_context(hints)
            planning_mode = "guided_llm"
            print(f"[LLMPlannerStrategy] 🧠 Injected {len(hints)} MemoryEpisodeHint(s) into PromptBuilder context ({planning_mode}).")

        # 1. Ask Inference Layer for Advice (with memory context if available)
        result = await self.inference.infer(interaction, memory)
        
        # 2. Apply Confidence Policy (Rule: The Planner decides, not the model)
        if result.confidence < getattr(self.policy, "clarify_threshold", 0.4):
            intent = GenericIntent("UnknownIntent", result.confidence, {})
        elif result.confidence < getattr(self.policy, "accept_threshold", 0.7):
            intent = GenericIntent("ClarificationIntent", result.confidence, result.entities)
        else:
            # High confidence, trust the inference result
            if result.intent == "GreetingIntent":
                intent = GreetingIntent(confidence=result.confidence, query=interaction.payload)
            elif result.intent == "SystemIntent":
                intent = SystemIntent(confidence=result.confidence, command=result.entities.get("command", ""))
            else:
                intent = GenericIntent(name=result.intent, confidence=result.confidence, entities=result.entities)
            
        decision = PlanningDecision(
            intent=intent,
            confidence=result.confidence,
            reasoning=result.reasoning_notes or f"Inferred by LLM ({planning_mode})",
            requires_approval=(result.confidence < 0.5)
        )
        setattr(decision, "planning_mode", planning_mode)
        setattr(decision, "experience_context_injected", bool(experience_context))
        return decision

    def create_plan(self, decision: PlanningDecision, interaction: InteractionEnvelope, session_id: str) -> ExecutionPlan:
        intent = decision.intent
        workflows = []
        
        # Deterministic Mapping based on Intent type
        if isinstance(intent, GreetingIntent):
            workflows.append(WorkflowRequest(
                action="text_response", 
                correlation_id=interaction.correlation_id,
                parameters={"text": "Hello! I am your AI companion powered by LLM inference."},
                policy=ExecutionPolicy(timeout=2.0)
            ))
        elif isinstance(intent, GenericIntent):
            if intent.subtype == "CreateReminder":
                time_val = intent.entities.get("time", "unknown time")
                workflows.append(WorkflowRequest(
                    action="text_response", 
                    correlation_id=interaction.correlation_id,
                    parameters={"text": f"I will remind you at {time_val}."},
                    policy=ExecutionPolicy(timeout=2.0)
                ))
            elif intent.subtype == "MathIntent":
                expr = intent.entities.get("expression", "")
                workflows.append(WorkflowRequest(
                    action="text_response", 
                    correlation_id=interaction.correlation_id,
                    parameters={"text": f"I see you want to calculate {expr}."},
                    policy=ExecutionPolicy(timeout=2.0)
                ))
            elif intent.subtype == "ClarificationIntent":
                workflows.append(WorkflowRequest(
                    action="text_response", 
                    correlation_id=interaction.correlation_id,
                    parameters={"text": "Could you clarify what time you meant?"},
                    policy=ExecutionPolicy(timeout=2.0)
                ))
            else:
                workflows.append(WorkflowRequest(
                    action="text_response", 
                    correlation_id=interaction.correlation_id,
                    parameters={"text": "I didn't quite understand that."},
                    policy=ExecutionPolicy(timeout=2.0)
                ))

        return ExecutionPlan(
            intent=intent,
            workflows=workflows,
            decision_quality=decision.confidence,
            approval=ApprovalRequirement(required=getattr(decision, "requires_approval", False))
        )
