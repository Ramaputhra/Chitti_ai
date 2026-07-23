from typing import List, Tuple
from desktop.models.inference import InferenceRequest, ContextItem, ContextPriority, CapabilityResultItem, ResponseMode

class PromptBuilder:
    """
    Rule 34: Prompt Assembly Is Centralized.
    Purely deterministic. No provider logic, no API calls.
    Uses XML for clear boundaries.
    """
    
    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Heuristic for MVP: 1 token ~= 4 chars."""
        return len(text) // 4
        
    @staticmethod
    def _format_mode_instruction(mode: ResponseMode) -> str:
        if mode == ResponseMode.CHAT:
            return "Respond conversationally to the user based on the context."
        elif mode == ResponseMode.SUMMARIZE:
            return "Summarize the supplied context."
        elif mode == ResponseMode.PLAN:
            return "Produce executable steps based on the planner goal."
        return f"Follow the instruction for mode: {mode.value}."
        
    @staticmethod
    def build(request: InferenceRequest, budget_tokens: int = 4096) -> str:
        # Static blocks
        system_block = f"<SYSTEM_PERSONA>\n{request.system_persona}\n</SYSTEM_PERSONA>\n"
        goal_block = f"<PLANNER_GOAL>\n{request.planner_goal}\n</PLANNER_GOAL>\n"
        mode_block = f"<INSTRUCTION>\n{PromptBuilder._format_mode_instruction(request.response_mode)}\n</INSTRUCTION>\n"
        user_block = f"<USER>\n{request.user_message}\n</USER>\n"
        
        static_text = system_block + goal_block + mode_block + user_block
        tokens_used = PromptBuilder._estimate_tokens(static_text)
        
        # Reserve 500 for the actual LLM output response
        remaining_budget = budget_tokens - tokens_used - 500
        
        # Group dynamic context by priority
        high = []
        medium = []
        low = []
        
        # Capability Results are HIGH
        for c in request.capability_results:
            xml = f'<CAPABILITY_RESULT id="{c.id}" status="{c.status}">\n{c.content}\n</CAPABILITY_RESULT>\n'
            high.append(xml)
            
        for m in request.memory_context:
            xml = f"<MEMORY>\n{m.content}\n</MEMORY>\n"
            if m.priority == ContextPriority.HIGH: high.append(xml)
            elif m.priority == ContextPriority.MEDIUM: medium.append(xml)
            else: low.append(xml)
            
        for a in request.awareness_context:
            xml = f"<AWARENESS>\n{a.content}\n</AWARENESS>\n"
            if a.priority == ContextPriority.HIGH: high.append(xml)
            elif a.priority == ContextPriority.MEDIUM: medium.append(xml)
            else: low.append(xml)
            
        # Append in priority order until budget is exhausted
        dynamic_xml = ""
        
        for pool in [high, medium, low]:
            for item_xml in pool:
                item_tokens = PromptBuilder._estimate_tokens(item_xml)
                if remaining_budget >= item_tokens:
                    dynamic_xml += item_xml
                    remaining_budget -= item_tokens
                else:
                    # Budget exhausted, trim lower priority context
                    break
                    
        return system_block + goal_block + mode_block + dynamic_xml + user_block
