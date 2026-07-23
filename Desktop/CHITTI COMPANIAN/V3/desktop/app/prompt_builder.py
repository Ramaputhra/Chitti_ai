import hashlib
from desktop.models.inference import PromptContext, PromptMetadata
from desktop.app.prompt_templates import PromptTemplates

class PromptBuilder:
    """
    Constructs prompts exclusively from deterministic inputs.
    (Rule 188: Prompt Construction Is Deterministic)
    """
    
    def __init__(self, budgeter=None):
        self.budgeter = budgeter
        
    def build(self, template_name: str, raw_context: PromptContext) -> tuple[str, PromptMetadata]:
        # Stage 1: Budget and Trim Context
        # (Budgeting is now handled prior to PromptBuilder)
        context = raw_context
            
        # Stage 2: Retrieve Template
        if template_name == "IntentClassification":
            template = PromptTemplates.INTENT_CLASSIFICATION
            version = "v1.4.0"
        else:
            raise ValueError(f"Unknown template: {template_name}")
            
        # Stage 3: Composition
        prompt = template.format(
            system_rules=context.system_rules,
            session_context=context.session_context,
            working_memory="\\n".join(context.working_memory),
            recent_messages="\\n".join(context.recent_messages),
            user_input=context.current_input
        )
        
        # Stage 4: Cryptographic Hashing for Telemetry
        content_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:12]
        
        metadata = PromptMetadata(
            version=version,
            content_hash=content_hash,
            template_name=template_name
        )
        
        return prompt, metadata

    @staticmethod
    def format_experience_context(hints: List[Any]) -> str:
        """
        COG-31B: Centralized prompt serialization for MemoryEpisodeHint domain models.
        Formats ranked experiences into anonymized XML without exposing episode_id,
        raw ExecutionPlans, or internal storage identifiers (Rule 37/40 & COG-31B Refinement).
        """
        if not hints:
            return ""

        xml_parts = ["<historical_experiences>"]
        for rank, hint in enumerate(hints, start=1):
            exp_level = getattr(hint, "experience_level", "MEDIUM")
            level_str = getattr(exp_level, "value", str(exp_level))
            ep_score = getattr(hint, "episode_score", 1.0)
            intent_sum = getattr(hint, "intent_summary", "")
            wf_sum = getattr(hint, "workflow_summary", "")
            outcome_sum = getattr(hint, "verified_outcome", "VERIFIED_SUCCESS")
            param_sum = getattr(hint, "parameter_summary", {}) or {}
            
            params_str = ", ".join(f'{k}="{v}"' for k, v in param_sum.items())
            xml_parts.append(
                f'  <experience rank="{rank}" level="{level_str}" score="{ep_score:.2f}">\n'
                f'    <intent>{intent_sum}</intent>\n'
                f'    <workflow>{wf_sum}</workflow>\n'
                f'    <parameters>{params_str}</parameters>\n'
                f'    <outcome>{outcome_sum}</outcome>\n'
                f'  </experience>'
            )
        xml_parts.append("</historical_experiences>")
        return "\n".join(xml_parts)
