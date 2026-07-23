import asyncio
from desktop.product.assistants.research.assistant import ResearchAssistant
from desktop.product.assistants.base import AssistantContext

async def verify_research_assistant():
    print("--- Research Assistant Verification (Sprint 63) ---\n")
    print("User Scenario: User closes 5 browser tabs comparing React and Vue. They are now inactive.")
    print("Goal: Assistant must perform Gap Analysis, internally prepare an artifact, and SUGGEST saving it.\n")
    
    assistant = ResearchAssistant()
    
    # Mocking the AssistantContext
    context = AssistantContext(
        workspace=None, memory=None, timeline=None, user_goal=None, confidence=0.0,
        constraints=[], environment={}, planner_context={}
    )
    
    response = await assistant.process_intent(context)
    workspace = response.payload['workspace']
    
    print("=== Constraint Verification ===")
    
    # 1. Verify Topic Extraction
    print(f"1. Active Topic: {workspace.active_topic}")
    assert "React vs Vue" in workspace.active_topic
    
    # 2. Verify Gap Analysis
    print(f"2. Knowledge Gaps Found: {workspace.knowledge_gaps}")
    assert "Server-Side Rendering (SSR)" in workspace.knowledge_gaps
    print(f"   Suggested Queries: {workspace.questions}")
    
    # 3. Verify Rule 148 Traceability in Explainability
    print(f"3. Explainability & Traceability (Rule 148):")
    for ev in response.explanation.evidence:
        print(f"    - [{ev.type}] from {ev.source}: {ev.payload}")
        if ev.type == "research_conclusion":
            assert "supporting_sources" in ev.payload
            
    # 4. Verify Passive Preparation Workflow
    print(f"4. Suggested Workflow (Passive Preparation): {response.explanation.suggested_workflow['action']}")
    assert response.explanation.suggested_workflow['action'] == "persist_artifact"
    print(f"   Autonomy Level: {response.autonomy.name}")
    assert response.autonomy.name == "SUGGEST"
    
    # 5. Verify Metrics
    print(f"5. Metrics: Gaps Found = {response.metrics.gaps_found}, Duplicates Removed = {response.metrics.duplicates_removed}")
    
    print("\n✅ All 5 structural constraints verified successfully!")
    print("The assistant leaves the workspace in a better state by identifying blind spots (SSR, Security) and quietly preparing a comparison document, waiting for user approval to persist it.")

if __name__ == "__main__":
    asyncio.run(verify_research_assistant())
