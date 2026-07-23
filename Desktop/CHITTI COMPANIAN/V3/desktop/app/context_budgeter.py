from typing import List
from desktop.models.inference import PromptContext
from desktop.models.cognition import SelectedContext, ContextSelectionPolicy, MemoryClass

class ContextBudgeter:
    """
    Owns token estimation, truncation, and memory selection.
    Ensures prompts always fit within the provider's max_context window.
    """
    def __init__(self, max_context: int):
        self.max_context = max_context
        
    def _estimate_tokens(self, text: str) -> int:
        # A simple heuristic for tokens until a real tokenizer (e.g. tiktoken) is added.
        # ~4 chars per token.
        return len(text) // 4
        
    def budget_and_trim(self, selected: SelectedContext, policy: ContextSelectionPolicy, system_rules: str, current_input: str) -> PromptContext:
        """
        Enforces token limits following the deterministic policy order.
        """
        system_tokens = self._estimate_tokens(system_rules)
        input_tokens = self._estimate_tokens(current_input)
        
        remaining = self.max_context - (system_tokens + input_tokens)
        
        final_working_memory: List[str] = []
        final_recent_messages: List[str] = []
        final_facts: List[str] = []
        final_episodes: List[str] = []
        final_session_context: str = ""
        discarded = 0
        
        def _fill(source_list: List[str], target_list: List[str], current_remaining: int) -> int:
            nonlocal discarded
            for item in source_list:
                tokens = self._estimate_tokens(item)
                if tokens <= current_remaining:
                    target_list.append(item)
                    current_remaining -= tokens
                else:
                    discarded += 1
            return current_remaining

        # Fill iteratively based on explicit deterministic policy
        for priority in policy.priority_order:
            if remaining <= 0:
                discarded += 1
                continue
                
            if priority == MemoryClass.WORKING_MEMORY:
                remaining = _fill(selected.working_memory, final_working_memory, remaining)
            elif priority == MemoryClass.RECENT_CONVERSATION:
                remaining = _fill(selected.recent_messages, final_recent_messages, remaining)
            elif priority == MemoryClass.FACT:
                remaining = _fill(selected.facts, final_facts, remaining)
            elif priority == MemoryClass.EPISODE:
                remaining = _fill(selected.episodes, final_episodes, remaining)
            elif priority == MemoryClass.SESSION_CONTEXT:
                tokens = self._estimate_tokens(selected.session_context)
                if tokens <= remaining:
                    final_session_context = selected.session_context
                    remaining -= tokens
                else:
                    discarded += 1
        
        return PromptContext(
            system_rules=system_rules,
            recent_messages=final_recent_messages,
            working_memory=final_working_memory,
            session_context=final_session_context,
            current_input=current_input
        )
