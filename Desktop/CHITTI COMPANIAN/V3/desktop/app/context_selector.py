from typing import List, Tuple
from desktop.models.interaction import InteractionEnvelope
from desktop.models.memory import MemorySnapshot
from desktop.models.cognition import ContextScore, ContextSelectionPolicy, SelectedContext, MemoryClass

class RuleBasedContextSelector:
    """
    Selects and prioritizes context deterministically based on keyword overlap, recency, and authority.
    Rule 192: Context selectors rank and prioritize existing memory for inference.
    """
    def __init__(self, policy: ContextSelectionPolicy):
        self.policy = policy
        
    def _score_fact(self, fact: str, interaction: InteractionEnvelope) -> ContextScore:
        # Simple deterministic scoring
        # In Sprint 90 this would use semantic similarity
        payload_lower = interaction.payload.lower()
        relevance = 0.5 if any(word in fact.lower() for word in payload_lower.split()) else 0.0
        
        # Artificial authority if the fact is a known high-priority entity
        authority = 1.0 if "name is" in fact.lower() or "preference" in fact.lower() else 0.0
        
        return ContextScore(
            relevance=relevance,
            recency=1.0, # Mock recency
            authority=authority,
            stability=1.0, # Facts are stable
            source=0.5
        )

    def select(self, interaction: InteractionEnvelope, memory: MemorySnapshot) -> SelectedContext:
        # 1. Working memory is always high priority, no scoring needed for this sprint
        working_memory = ["System state: Active"]
        
        # 2. Recent conversation
        recent_messages = ["User: " + interaction.payload]
        
        # 3. Facts: Score and sort
        raw_facts = memory.facts if hasattr(memory, 'facts') else []
        scored_facts: List[Tuple[ContextScore, str]] = []
        for fact in raw_facts:
            score = self._score_fact(fact, interaction)
            scored_facts.append((score, fact))
            
        # Sort facts primarily by total score, highest first
        scored_facts.sort(key=lambda x: x[0].total, reverse=True)
        sorted_facts = [f for s, f in scored_facts]
        
        # 4. Episodes (Mock empty for now)
        episodes = []
        
        # 5. Session Context
        session_context = "Session started 10m ago."
        
        return SelectedContext(
            working_memory=working_memory,
            recent_messages=recent_messages,
            facts=sorted_facts,
            episodes=episodes,
            session_context=session_context,
            discarded_count=0 # Budgeter determines final discard
        )
