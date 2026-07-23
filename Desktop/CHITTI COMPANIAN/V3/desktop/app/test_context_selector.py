import asyncio
from desktop.models.interaction import InteractionEnvelope
from desktop.models.memory import MemorySnapshot
from desktop.models.cognition import ContextSelectionPolicy, MemoryClass
from desktop.app.context_selector import RuleBasedContextSelector
from desktop.app.context_budgeter import ContextBudgeter

def test_context_selection():
    policy = ContextSelectionPolicy([
        MemoryClass.WORKING_MEMORY,
        MemoryClass.RECENT_CONVERSATION,
        MemoryClass.FACT,
        MemoryClass.EPISODE,
        MemoryClass.SESSION_CONTEXT
    ])
    selector = RuleBasedContextSelector(policy)
    
    # 1. Scoring Test
    interaction = InteractionEnvelope(id="1", payload="What is my name?")
    memory = MemorySnapshot(episodes=[], facts=["User is testing the system.", "User's name is Alice."])
    # Dynamically patching MemorySnapshot for facts since facts might not be directly in the type yet
    memory.facts = ["User is testing the system.", "User's name is Alice."]
    
    selected = selector.select(interaction, memory)
    
    # "User's name is Alice" should be scored higher because of the "name is" authority and keyword overlap
    assert len(selected.facts) == 2
    assert "name is Alice" in selected.facts[0], "Highest scored fact should be first"
    
    # 2. Budgeter Priority Test (Working Memory wins over Facts)
    budgeter = ContextBudgeter(max_context=15) # Very small budget
    context = budgeter.budget_and_trim(
        selected=selected,
        policy=policy,
        system_rules="Sys",
        current_input="Input"
    )
    
    assert len(context.working_memory) > 0, "Working memory should be preserved"
    assert len(context.facts) == 0, "Facts should be discarded due to budget"
    
    print("✅ Context Selector tests passed")

if __name__ == "__main__":
    print("--- Running Context Selector Tests (Sprint 87) ---\n")
    test_context_selection()
    print("\n✅ All Sprint 87 tests passed.")
