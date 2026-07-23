import time
from typing import Dict, Any, List
from desktop.product.assistants.base import BaseAssistant, AssistantResponse, AutonomyLevel, Explanation, Evidence, AssistantContext, AssistantMetrics
from desktop.product.assistants.coding.models import DetectedGoal
from desktop.product.assistants.meeting.models import (
    MeetingPhase, ContextTransition, MeetingContext, MeetingBrief, MeetingTimeline, MeetingOutcome
)

class MeetingAssistant(BaseAssistant):
    """
    Solves the human job: "Context switching into meetings prepared, capturing decisions, and smoothly returning to deep work."
    The Context Transition Assistant.
    """
    def __init__(self, phase: MeetingPhase):
        self.phase = phase

    async def process_intent(self, context: AssistantContext) -> AssistantResponse:
        metrics = AssistantMetrics()
        start_time = time.time()
        
        # 1. Observation (Rule 151)
        # e.g., Calendar event "Sync with Design Team" is happening now or just ended.
        
        # 2. Context Recovery
        meeting_context = MeetingContext(
            meeting_title="Architecture Review",
            participants=["Alice", "Bob"],
            related_topics=["Planner Runtime", "Immutability"],
            related_projects=["CHITTI v2"],
            current_workspace="Editing assistant.py in Meeting Assistant",
            expected_decisions=["Finalize Rule 154"],
            open_questions=[],
            time_constraints="30 mins",
            importance="High"
        )
        
        # 3. Transition Analysis (Unique to Meeting Assistant)
        transition = ContextTransition(
            source_context="Deep Work: Coding",
            target_context="Meeting: Architecture Review",
            preserved_state_id="workspace_snapshot_1234", # Managed by Continuity Engine
            restoration_plan=["Restore VSCode to assistant.py", "Resume paused background tasks"],
            confidence=1.0
        )
        
        # 4. Domain Analysis (Phase-dependent behavior)
        if self.phase == MeetingPhase.PREPARING:
            goal_text = "Prepare user for Architecture Review and save current workspace."
            brief = MeetingBrief(
                agenda="Review Planner Runtime immutability",
                participants=meeting_context.participants,
                previous_decisions=["Rule 113 adopted"],
                open_questions=["Is Rule 154 required?"],
                relevant_documents=["ARCHITECTURE_FROZEN_v3.0.md"],
                risks=["Scope creep"],
                recommended_focus="Agree on Rule 154 before leaving."
            )
            payload = {"brief": brief, "transition": transition}
            suggestion_reason = "Your meeting starts in 5 minutes. I have prepared a brief and can save your IDE state so you can resume coding immediately afterward."
            suggested_action = "save_workspace_state"
            
        elif self.phase == MeetingPhase.ACTIVE:
            goal_text = "Silent Context Monitoring."
            payload = {}
            suggestion_reason = "Monitoring meeting for context."
            suggested_action = "none"
            
        elif self.phase == MeetingPhase.RETURN_TO_WORK:
            goal_text = "Restore previous context and update Knowledge Runtime."
            outcome = MeetingOutcome(
                decisions=["Rule 154 adopted: Assistants Preserve Cognitive Continuity"],
                action_items=["Implement Rule 154 in Meeting Assistant"],
                new_questions=[],
                knowledge_updates=["Added Rule 154 to AGENTS.md"],
                followups=[],
                affected_projects=["CHITTI v2"],
                confidence=1.0
            )
            # Rule 154: Restore working context through platform runtimes (Continuity Engine)
            payload = {"outcome": outcome, "transition": transition}
            suggestion_reason = "The meeting has concluded. I've captured the decisions. Shall I restore your IDE so you can continue coding?"
            suggested_action = "restore_workspace_state" # Executed by Planner -> Continuity Engine
            
        else:
            goal_text = f"Handle phase {self.phase.name}"
            payload = {}
            suggestion_reason = ""
            suggested_action = ""

        # 5. Goal Detection
        goal = DetectedGoal(
            goal=goal_text,
            confidence=1.0,
            evidence=[{"source": "Calendar", "status": self.phase.name}],
            alternatives={},
            missing_information=[]
        )
        
        # 6. Passive Preparation & Suggestion
        explanation = Explanation(
            reason=suggestion_reason,
            evidence=[
                Evidence(
                    type="context_transition",
                    source="TransitionAnalysis",
                    confidence=1.0,
                    payload={"transition": transition.__dict__}
                )
            ],
            confidence=goal.confidence,
            suggested_workflow={"action": suggested_action, "payload": payload}
        )
        
        metrics.planning_time = (time.time() - start_time) * 1000
        
        return AssistantResponse(
            goal=goal.goal,
            autonomy=AutonomyLevel.SUGGEST,
            explanation=explanation,
            metrics=metrics,
            payload=payload
        )
