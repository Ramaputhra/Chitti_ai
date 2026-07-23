import asyncio
from desktop.product.assistants.meeting.assistant import MeetingAssistant
from desktop.product.assistants.meeting.models import MeetingPhase
from desktop.product.assistants.base import AssistantContext

async def verify_meeting_assistant():
    print("--- Meeting Assistant Verification (Sprint 66) ---\n")
    print("Goal: Assistant acts as a Context Transition Assistant, applying Rule 154.\n")
    
    context = AssistantContext(
        workspace=None, memory=None, timeline=None, user_goal=None, confidence=0.0,
        constraints=[], environment={}, planner_context={}
    )
    
    # 1. Verify PREPARING phase
    print("=== Phase: PREPARING ===")
    assistant_prep = MeetingAssistant(phase=MeetingPhase.PREPARING)
    response_prep = await assistant_prep.process_intent(context)
    brief = response_prep.payload['brief']
    transition_prep = response_prep.payload['transition']
    
    print(f"Goal: {response_prep.goal}")
    print(f"Prepared Artifact: MeetingBrief (Focus: {brief.recommended_focus})")
    print(f"Rule 154 Transition Plan: Save '{transition_prep.source_context}' to ID '{transition_prep.preserved_state_id}'")
    print(f"Suggested Action: {response_prep.explanation.suggested_workflow['action']}\n")
    
    assert response_prep.explanation.suggested_workflow['action'] == "save_workspace_state"
    
    # 2. Verify RETURN_TO_WORK phase
    print("=== Phase: RETURN_TO_WORK ===")
    assistant_return = MeetingAssistant(phase=MeetingPhase.RETURN_TO_WORK)
    response_return = await assistant_return.process_intent(context)
    outcome = response_return.payload['outcome']
    transition_return = response_return.payload['transition']
    
    print(f"Goal: {response_return.goal}")
    print(f"Knowledge Update (Feedback Loop): {outcome.knowledge_updates[0]}")
    print(f"Rule 154 Transition Plan: {transition_return.restoration_plan[0]}")
    print(f"Suggested Action: {response_return.explanation.suggested_workflow['action']}\n")
    
    assert response_return.explanation.suggested_workflow['action'] == "restore_workspace_state"
    
    print("✅ All structural constraints verified successfully!")
    print("The assistant correctly delegates Continuity Bridge operations to the platform, preparing Briefs and Outcomes while keeping the user in flow.")

if __name__ == "__main__":
    asyncio.run(verify_meeting_assistant())
