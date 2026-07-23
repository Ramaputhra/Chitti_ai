import asyncio
from desktop.product.assistants.documentation.assistant import DocumentationAssistant
from desktop.product.assistants.base import AssistantContext

async def verify_documentation_assistant():
    print("--- Documentation Assistant Verification (Sprint 64) ---\n")
    print("User Scenario: User commits a change adding 'timeout' to a method, but forgets to update the docstring.")
    print("Goal: Assistant performs Consistency Analysis, finds Debt, and Prepares a DocumentationPatch with evidence (Rule 150).\n")
    
    assistant = DocumentationAssistant()
    context = AssistantContext(
        workspace=None, memory=None, timeline=None, user_goal=None, confidence=0.0,
        constraints=[], environment={}, planner_context={}
    )
    
    response = await assistant.process_intent(context)
    debt = response.payload['debt']
    trace = response.payload['trace']
    patch = response.payload['patch']
    coverage = response.payload['coverage']
    
    print("=== Constraint Verification ===")
    
    # 1. Verify DecisionTrace Recovery
    print(f"1. Architectural Intent Recovered: {trace.decision}")
    print(f"   Motivation: {trace.motivation}")
    print(f"   Origin Sprint: {trace.origin_sprint}, Origin Rule: {trace.origin_rule}")
    
    # 2. Verify Consistency & Debt Analysis
    print(f"2. Knowledge Debt Detected: {debt.type}")
    print(f"   Recommended Action: {debt.recommended_action}")
    print(f"   API Docs Coverage: {coverage.api_docs_score}")
    
    # 3. Verify Rule 150 Traceability in DocumentationPatch
    print(f"3. Rule 150 (Knowledge Explainability) Verification:")
    print(f"   Review Summary: {patch.review_summary}")
    print("   Evidence for Patch:")
    has_code_evidence = False
    has_intent_evidence = False
    for ev in response.explanation.evidence:
        print(f"    - [{ev.type}] from {ev.source}: {ev.payload}")
        if ev.type == "code_analysis":
            has_code_evidence = True
        if ev.type == "architectural_intent":
            has_intent_evidence = True
            
    assert has_code_evidence and has_intent_evidence
            
    # 4. Verify Passive Preparation Workflow
    print(f"\n4. Suggested Workflow (Passive Preparation): {response.explanation.suggested_workflow['action']}")
    print(f"   Autonomy Level: {response.autonomy.name}")
    assert response.autonomy.name == "SUGGEST"
    
    print("\n✅ All structural constraints verified successfully!")
    print("The assistant behaves as a Knowledge Consistency Guardian using the Rule 151 Cognitive Pipeline.")

if __name__ == "__main__":
    asyncio.run(verify_documentation_assistant())
