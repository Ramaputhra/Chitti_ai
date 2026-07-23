import asyncio
from uuid import uuid4
from desktop.models.interaction import InteractionEnvelope
from desktop.models.memory import MemorySnapshot
from desktop.platform.strategies.deterministic_planner import DeterministicPlannerStrategy
from desktop.platform.strategies.llm_planner import LLMPlannerStrategy, GenericIntent
from desktop.platform.strategies.llm_inference import LLMInferenceStrategy
from desktop.platform.inference.inference.mock_llm import MockLLMProvider
from desktop.models.intents import GreetingIntent, SystemIntent

async def run_benchmark():
    print("--- Running Planner Benchmark Suite (Sprint 83) ---\n")
    
    # Setup
    deterministic_planner = DeterministicPlannerStrategy()
    mock_llm = MockLLMProvider()
    inference_strategy = LLMInferenceStrategy(mock_llm)
    llm_planner = LLMPlannerStrategy(inference_strategy)
    
    test_cases = [
        # Tier 1: Deterministic
        ("Hello", "GreetingIntent", []),
        ("What is 2+2", "MathIntent", ["expression"]),
        
        # Tier 2: Parameter Extraction
        ("Remind me in 20 minutes", "CreateReminder", ["time"]),
        ("Call mom tomorrow", "CreateReminder", ["time", "person"]),
        
        # Tier 3: Ambiguity
        ("Remind me later", "ClarificationIntent", ["missing_parameter"]),
        
        # Tier 4: Negative/Fallback
        ("asdfasdf", "UnknownIntent", []),
    ]
    
    memory = MemorySnapshot(episodes=[], facts=[])
    
    for input_text, expected_intent, expected_entities in test_cases:
        print(f"\n[Test] Input: '{input_text}'")
        
        interaction = InteractionEnvelope(
            id=str(uuid4()),
            correlation_id=str(uuid4()),
            payload=input_text,
            origin="Benchmark",
            transport="Benchmark"
        )
        
        # Test Deterministic (if supported by its simple regex rules, we skip unsupported ones for it, 
        # but for now we'll just run LLM Planner to prove it works).
        print("  -> Running LLM Planner...")
        decision = await llm_planner.plan(interaction, memory)
        intent = decision.intent
        
        # Validate Intent
        intent_name = intent.__class__.__name__
        if isinstance(intent, GenericIntent):
            intent_name = intent.name
            
        print(f"     Got Intent: {intent_name} (Expected: {expected_intent})")
        assert intent_name == expected_intent, f"Expected {expected_intent}, got {intent_name}"
        
        # Validate Entities
        if isinstance(intent, GenericIntent):
            for ent in expected_entities:
                assert ent in intent.entities, f"Expected entity '{ent}' not found in {intent.entities}"
            print(f"     Got Entities: {intent.entities}")
            
        # Create Plan
        plan = llm_planner.create_plan(decision, interaction, "test_session")
        print(f"     Generated {len(plan.workflows)} workflows.")
        assert len(plan.workflows) > 0, "No workflows generated for intent."

    print("\n✅ All Benchmark Tests Passed for LLMPlannerStrategy.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
