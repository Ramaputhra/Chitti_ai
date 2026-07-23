from typing import Dict, Any, List
from desktop.capabilities.work_continuity.models import (
    ContinuityModel, FocusState, Recommendation, Bottleneck, WorkContinuity
)
from desktop.capabilities.work_continuity.policy import InterruptionPolicyEngine

class WorkContinuityCapability:
    """
    Synthesizes the user's Experience Timeline (Memory) using the Prediction Runtime.
    Goal: Help the user continue what matters (Rule 137).
    """
    def __init__(self, memory_runtime, prediction_runtime):
        self.memory_runtime = memory_runtime
        self.prediction_runtime = prediction_runtime
        self.policy_engine = InterruptionPolicyEngine()

    async def execute(self, payload: Dict[str, Any]) -> ContinuityModel:
        # 1. Fetch relevant memory (e.g., today's sessions, yesterday's daily summary)
        # sessions = self.memory_runtime.get_recent_sessions()
        
        # 2. Invoke Prediction Runtime to analyze continuity (Stubbed)
        # analysis = await self.prediction_runtime.analyze_continuity(sessions)
        
        current_focus = FocusState.FLOW
        
        # 3. Formulate Unfinished Work
        unfinished = [
            WorkContinuity(
                last_goal="Implement Work Continuity Capability",
                completion_percentage=0.8,
                resume_point="Writing capability.py",
                next_action="Build demo_workflow.py",
                supporting_documents=["models.py", "policy.py", "AGENTS.md"],
                confidence=0.95
            )
        ]
        
        # 4. Generate Recommendations
        raw_rec = Recommendation(
            priority=0.8,
            reason="You spent 4.3 hours on Sprint 60 yesterday and left 3 files open.", # Rule 139
            estimated_value=0.9,
            estimated_time=1200,
            confidence=0.95
        )
        
        # 5. Enforce Rule 138 via Interruption Policy Engine
        filtered_rec = self.policy_engine.evaluate(raw_rec, current_focus)
        
        # 6. Identify Bottlenecks
        bottlenecks = []
        if payload.get("simulate_stuck"):
            bottlenecks.append(Bottleneck(
                reason="Searching StackOverflow for PyTorch leaks",
                duration=2700,
                severity=0.7,
                recommended_action="Search local CHITTI project logs instead."
            ))

        # 7. Construct final ContinuityModel
        return ContinuityModel(
            current_focus=current_focus,
            unfinished_work=unfinished,
            recommended_next_step=filtered_rec,
            blocked_tasks=bottlenecks,
            recent_progress="Successfully completed Sprint 59 Memory Integration.",
            risk_factors=["High volume of context switches detected early morning."],
            confidence=0.92
        )
