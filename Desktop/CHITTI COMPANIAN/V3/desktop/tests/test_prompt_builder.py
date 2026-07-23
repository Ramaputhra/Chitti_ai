import hashlib
from desktop.models.inference import PromptContext, PromptMetadata
from desktop.app.prompt_builder import PromptBuilder
from desktop.app.context_budgeter import ContextBudgeter

def test_prompt_reproducibility():
    """
    Test 1: Identical inputs must produce the exact same prompt hash.
    (Rule 188: Prompt Construction Is Deterministic)
    """
    builder = PromptBuilder(budgeter=ContextBudgeter(max_context=4096))
    
    context = PromptContext(
        system_rules="System Rule 1",
        session_context="Session 1",
        working_memory=["Memory 1"],
        recent_messages=["Hi"],
        current_input="Test"
    )
    
    prompt1, metadata1 = builder.build("IntentClassification", context)
    prompt2, metadata2 = builder.build("IntentClassification", context)
    
    assert prompt1 == prompt2, "Prompts must be identical"
    assert metadata1.content_hash == metadata2.content_hash, "Hashes must match exactly"
    print("✅ Test 1: Prompt Reproducibility passed")

def test_provider_independence():
    """
    Test 2: Ensure core prompt meaning is independent of how providers might eventually format it.
    (Currently we only have one string format, but this test sets up the pattern).
    """
    builder = PromptBuilder(budgeter=ContextBudgeter(max_context=4096))
    
    context = PromptContext(
        system_rules="Core Rule",
        session_context="Session",
        working_memory=["WM"],
        recent_messages=["Msg"],
        current_input="Input"
    )
    
    prompt, metadata = builder.build("IntentClassification", context)
    
    assert "Core Rule" in prompt
    assert "Input" in prompt
    assert metadata.version == "v1.4.0"
    print("✅ Test 2: Provider Independence formatting checks passed")

if __name__ == "__main__":
    print("--- Running PromptBuilder Tests (Sprint 85) ---\n")
    test_prompt_reproducibility()
    test_provider_independence()
    print("\n✅ All PromptBuilder tests passed.")
