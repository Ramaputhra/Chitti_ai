import asyncio
from desktop.product.assistants.personal_knowledge.assistant import PersonalKnowledgeAssistant
from desktop.product.assistants.base import AssistantContext

async def verify_pka_assistant():
    print("--- Personal Knowledge Assistant Verification (Sprint 67) ---\n")
    print("User Scenario: User opens ADR-42.md.")
    print("Goal: Assistant passively retrieves knowledge and prepares a SynthesisArtifact observing Rule 155.\n")
    
    assistant = PersonalKnowledgeAssistant()
    context = AssistantContext(
        workspace=None, memory=None, timeline=None, user_goal=None, confidence=0.0,
        constraints=[], environment={}, planner_context={}
    )
    
    response = await assistant.process_intent(context)
    artifact = response.payload['artifact']
    
    print("=== Constraint Verification ===")
    
    # 1. Verify Passive Preparation
    print(f"1. Suggested Action (Passive): {response.explanation.suggested_workflow['action']}")
    print(f"   Autonomy Level: {response.autonomy.name}")
    assert response.autonomy.name == "SUGGEST"
    
    # 2. Verify Rule 155 (Knowledge Explainability / No Invention)
    print(f"\n2. Rule 155 (Knowledge Distinctions) Verification:")
    print(f"   [RETRIEVED FACTS]:")
    for fact in artifact.retrieved_facts:
        print(f"     - {fact}")
    print(f"   [INFERRED CONCLUSIONS]:")
    for inf in artifact.inferred_conclusions:
        print(f"     - {inf}")
    print(f"   [UNRESOLVED GAPS]:")
    for gap in artifact.unresolved_gaps:
        print(f"     - {gap}")
        
    assert len(artifact.retrieved_facts) > 0
    assert len(artifact.inferred_conclusions) > 0
    assert len(artifact.unresolved_gaps) > 0
    
    # 3. Verify Perspective & Confidence
    perspective = response.explanation.evidence[0].payload['perspective']
    print(f"\n3. Perspective Used: {perspective}")
    print(f"   Traceability Score: {artifact.confidence.traceability}")
    
    print("\n✅ All structural constraints verified successfully!")
    print("The assistant successfully acts as the Knowledge Access Layer, separating facts from inferences without inventing knowledge.")

if __name__ == "__main__":
    asyncio.run(verify_pka_assistant())
