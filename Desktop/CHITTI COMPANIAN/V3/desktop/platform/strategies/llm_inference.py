import json
from desktop.app.inference_contracts import IInferenceStrategy
from desktop.models.inference import InferenceResult, InferenceRequest
from desktop.models.interaction import InteractionEnvelope
from desktop.models.memory import MemorySnapshot
from desktop.app.prompt_templates import PromptTemplates
from desktop.app.inference_manager import InferenceManager
from desktop.app.inference_validator import InferenceValidator
from desktop.app.prompt_builder import PromptBuilder
from desktop.models.inference import PromptContext
from desktop.models.telemetry import InferenceTelemetryRecord, PromptReplayRecord
from desktop.app.inference_telemetry import InferenceTelemetry
from desktop.app.replay_logger import ReplayLogger
from desktop.app.context_selector import RuleBasedContextSelector
from desktop.models.cognition import ContextSelectionPolicy, MemoryClass

class LLMInferenceStrategy(IInferenceStrategy):
    """
    Uses an LLM Provider to perform cognitive inference.
    (Rule 183: Inference produces decisions, never side effects.)
    """
    def __init__(self, manager: InferenceManager, validator: InferenceValidator, builder: PromptBuilder, telemetry: InferenceTelemetry, replay_logger: ReplayLogger, context_selector: RuleBasedContextSelector = None):
        self.manager = manager
        self.validator = validator
        self.builder = builder
        self.telemetry = telemetry
        self.replay_logger = replay_logger
        self.context_selector = context_selector or RuleBasedContextSelector(ContextSelectionPolicy([
            MemoryClass.WORKING_MEMORY,
            MemoryClass.RECENT_CONVERSATION,
            MemoryClass.FACT,
            MemoryClass.EPISODE,
            MemoryClass.SESSION_CONTEXT
        ]))
        
    async def infer(self, interaction: InteractionEnvelope, memory: MemorySnapshot) -> InferenceResult:
        # 1. Select Context
        selected = self.context_selector.select(interaction, memory)
        
        # 2. Prepare Context Sections
        from desktop.app.context_budgeter import ContextBudgeter
        budgeter = ContextBudgeter(max_context=1000)
        
        system_rules = "You are CHITTI, a helpful deterministic companion."
        
        context = budgeter.budget_and_trim(
            selected=selected,
            policy=self.context_selector.policy,
            system_rules=system_rules,
            current_input=interaction.payload
        )
        
        # 3. Build Prompt (handles budgeting, formatting, and hashing)
        prompt, metadata = self.builder.build("IntentClassification", context)
        
        req = InferenceRequest(prompt=prompt, json_mode=True)
        
        # 4. Generate via Manager (handles routing/fallback)
        resp = await self.manager.generate(req)
        
        # 4. Validate and Parse Untrusted Input via Validator
        result = self.validator.validate(resp)
        
        # Attach the prompt metadata to the result for tracing
        result = InferenceResult(
            intent=result.intent,
            confidence=result.confidence,
            entities=result.entities,
            raw_response=result.raw_response,
            reasoning_notes=result.reasoning_notes,
            prompt_metadata=metadata
        )
        
        # Note: In a real flow, Planner Outcome is recorded *after* Planner finishes,
        # but for architectural tracing we record the Inference Outcome here.
        record = InferenceTelemetryRecord(
            correlation_id=interaction.id,
            interaction_id=interaction.id,
            plan_id=None,
            prompt_version=metadata.version,
            prompt_hash=metadata.content_hash,
            provider_name=resp.model_used,
            model_name=resp.model_used,
            latency_ms=resp.latency_ms,
            prompt_tokens=self.builder.budgeter._estimate_tokens(prompt) if self.builder.budgeter else 0,
            completion_tokens=resp.usage.get("completion_tokens", 0) if resp.usage else 0,
            validation_outcome="PASS" if result.intent != "UnknownIntent" else "FAIL",
            raw_confidence=result.confidence,
            planner_outcome="Pending" # Planner fills this later
        )
        self.telemetry.record(record)
        
        # Rule 190: Write full operational data separately
        import datetime
        replay = PromptReplayRecord(
            timestamp=datetime.datetime.now().isoformat(),
            prompt_hash=metadata.content_hash,
            provider_name=resp.model_used,
            model_name=resp.model_used,
            latency_ms=resp.latency_ms,
            prompt_tokens=record.prompt_tokens,
            completion_tokens=record.completion_tokens,
            confidence=result.confidence,
            request_payload=prompt,
            response_payload=resp.raw_response,
            validation_outcome=record.validation_outcome,
            planner_outcome="Pending"
        )
        self.replay_logger.log(replay)
        
        return result
