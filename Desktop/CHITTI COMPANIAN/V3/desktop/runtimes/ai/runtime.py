import logging
from typing import Any, Dict, List
from desktop.platform.shared.models.ai import LLMRequest, LLMResponse
from desktop.models.interaction import IntentResult
from desktop.runtimes.ai.intent_validator import IntentValidator

logger = logging.getLogger(__name__)

class AIRuntime:
    """
    AIRuntime sits between ConversationRuntime and InferenceRuntime.
    It is currently a thin delegation shell. In Phase 2, this will absorb
    context management, prompt assembly, token budgeting, and tool schema injection.
    """
    def __init__(self, inference_runtime: Any, cap_registry: Any = None):
        self.inference_runtime = inference_runtime
        self.cap_registry = cap_registry
        self.context = None
        
    async def initialize(self, context) -> bool:
        self.context = context
        return True

    async def start(self):
        logger.info("AIRuntime started.")
        return True
        
    async def stop(self):
        return True
        
    async def shutdown(self):
        return True

    def execute(self, request: LLMRequest) -> LLMResponse:
        """
        Delegates the compiled LLMRequest directly to InferenceRuntime.
        """
        logger.info("[AIRuntime] Passing request to InferenceRuntime...")
        # Currently just a pass-through
        return self.inference_runtime.execute(request)
        
    def generate(self, messages: List[Dict[str, str]], tools_enabled: bool = True) -> Dict[str, Any]:
        """
        Delegates raw generate requests (used currently by ConversationRuntime).
        """
        logger.info("[AIRuntime] Passing generate request to InferenceRuntime...")
        provider = self.inference_runtime.provider
        if hasattr(provider, "core") and hasattr(provider.core, "generate"):
            return provider.core.generate(messages, tools_enabled=tools_enabled)
        elif hasattr(provider, "generate"):
            # Mock or direct provider fallback
            import inspect
            sig = inspect.signature(provider.generate)
            if "tools_enabled" in sig.parameters:
                return provider.generate(messages, tools_enabled=tools_enabled)
            elif "messages" in sig.parameters:
                return provider.generate(messages)
        return {"text": "", "tool_calls": []}
        
    def resolve_intent(self, interaction: Any, source: str, session: Any = None) -> IntentResult:
        """
        Builds the prompt, invokes InferenceRuntime, and validates the semantic JSON.
        """
        logger.info(f"[AIRuntime] Resolving intent for interaction {interaction.original_text}")
        
        system_prompt = """
You are the CHITTI intent parser. Convert the user's request into a strict JSON object.

# CRITICAL RULE: NEVER INVENT INTENTS
You SHALL NEVER invent new intent names (e.g., QueryIntent, ExplanationIntent, SearchIntent, BrowserIntent). 
You MUST select EXACTLY ONE intent from the allowed lists below. If uncertain, select the closest supported intent.

# Intent Precedence Matrix (Highest to Lowest)
If a prompt matches multiple intents, always select the higher precedence intent:
1. LaunchAppIntent > CommandIntent
2. CloseAppIntent > CommandIntent
3. ResumeActivityIntent > LaunchAppIntent
4. StateQueryIntent > QuestionIntent
Specific intents ALWAYS take precedence over generic intents.

# Intent Decision Rules

## LaunchAppIntent
- Purpose: Opening or launching local desktop applications.
- Positive: "open calculator", "launch vscode", "start chrome", "start task manager"
- Negative: Do not use for scripts or terminal commands (use CommandIntent). Do not use to resume past work (use ResumeActivityIntent).

## CloseAppIntent
- Purpose: Closing, killing, or terminating local desktop applications/windows.
- Positive: Treat any of these verbs applied to an application as CloseAppIntent: close, exit, quit, kill, terminate, shut down. (e.g., "close calculator", "quit paint", "shut down spotify", "kill task manager").
- Negative: Do NOT classify closing apps as generic CommandIntent.

## CommandIntent
- Purpose: Executing specific catalog actions, system operations, or shell commands.
- Positive: "empty the trash", "run the backup script", "get_identity"
- Negative: Do not use for launching standard GUI apps (use LaunchAppIntent) or closing them (use CloseAppIntent).

## StateQueryIntent
- Purpose: Asking about the status, progress, or outcome of a recent system action/process.
- Positive: "did the backup finish?", "is the server still running?"
- Negative: Do not use for factual trivia (use QuestionIntent).

## DistanceIntent
- Purpose: Physical geospatial routing or physical distance between locations.
- Positive: "how far is paris from london", "distance to new york"

## QuestionIntent
- Purpose: Retrieve factual information already known by the LLM. 
- Positive: "What is photosynthesis?", "Who wrote Hamlet?", "How do airplanes fly?", "What is the deepest ocean?", "Explain quantum computing."
- Negative: The word "How" alone must NOT imply ReasoningIntent. Factual "How" questions belong here.

## ReasoningIntent
- Purpose: Derive a new answer through logic, mathematics, or calculation.
- Positive: "What is 15% of 80?", "Solve 2x = 10.", "Is 17 prime?", "Convert Fahrenheit to Celsius."
- Negative: Do not use for factual questions (use QuestionIntent). Math is never DistanceIntent.

## ResumeActivityIntent
- Purpose: Resuming past coding work, projects, or sessions.
- Positive: "resume my coding project", "bring back my workspace"

## ClarificationIntent
- Purpose: When the request is completely ambiguous and requires asking the user for more details.
- Positive: "do it", "fix this", "run"

## SmallTalkIntent
- Purpose: General greetings, pleasantries, casual conversation.
- Positive: "hello there", "good morning"

# JSON Output Format
Output ONLY raw JSON. No markdown formatting, no backticks.
Example: {"intent": "LaunchAppIntent", "confidence": 0.98, "parameters": {"app_command": "calc.exe"}}
"""
        from desktop.app.capability_contracts import CapabilityCatalog
        if self.cap_registry:
            catalog = CapabilityCatalog(self.cap_registry)
            system_prompt += "\n" + catalog.generate_summary() + "\n"
        elif hasattr(self, 'context') and self.context and hasattr(self.context, 'registry'):
            catalog = CapabilityCatalog(self.context.registry)
            system_prompt += "\n" + catalog.generate_summary() + "\n"
        messages = [
            {"role": "system", "content": system_prompt.strip()}
        ]
        
        if session and session.execution_context.last_success:
            # Just add lightweight context if the user is asking about it
            messages.append({"role": "system", "content": f"Recent Execution State:\n{session.execution_context.last_success}"})
            
        if session and session.recent_entities:
            entities_str = ", ".join([e.display for e in session.recent_entities])
            messages.append({"role": "system", "content": f"Recent Entities Context:\n{entities_str}"})
            
        if interaction.resolved_entities:
            # We have resolved entities, explicitly inform the LLM to use them for missing parameters
            entities_str = ", ".join([f"'{e.display}'" for e in interaction.resolved_entities])
            messages.append({"role": "system", "content": f"Entity Resolution Context:\nThe user's utterance contains ambiguous references. They likely refer to the following recent entities: {entities_str}.\nUse these to fill in any missing application or target parameters."})
            
        messages.append({"role": "user", "content": interaction.original_text})
        
        raw_response = self.generate(messages, tools_enabled=False)
        raw_json = raw_response.get("text", "")
        
        # Validate output via IntentValidator
        return IntentValidator.validate(raw_json, getattr(interaction, "id", "unknown"), source, interaction.original_text)

    def generate_response(self, session: Any, intent: str = "QuestionIntent") -> str:
        """
        Dynamically assembles a prompt based on session context via ContextAssembler.
        """
        logger.info(f"[AIRuntime] Generating response for session {session.session_id} with intent {intent}")
        
        system_prompt = "You are CHITTI, a helpful desktop AI companion. Be concise, friendly, and factual."
        
        from desktop.runtimes.conversation.context_assembler import ContextAssembler
        assembler = ContextAssembler()
        messages = assembler.assemble_prompt(session, intent, system_prompt)
            
        raw_response = self.generate(messages, tools_enabled=False)
        return raw_response.get("text", "I'm sorry, I'm having trouble processing that right now.")

    def stop(self):
        logger.info("AIRuntime stopped.")
