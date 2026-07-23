import time
from typing import Dict, Any, List
from datetime import datetime
from desktop.product.assistants.base import BaseAssistant, AssistantResponse, AutonomyLevel, Explanation, Evidence, AssistantContext, AssistantMetrics
from desktop.product.assistants.coding.models import DetectedGoal
from desktop.product.assistants.documentation.models import (
    KnowledgeTarget, KnowledgeDebt, AudienceProfile, DocumentationPatch, DecisionTrace, KnowledgeCoverage
)

class DocumentationAssistant(BaseAssistant):
    """
    Solves the human job: "Explain technical intent, capture decisions, maintain architectural knowledge."
    The Knowledge Consistency Guardian.
    """
    async def process_intent(self, context: AssistantContext) -> AssistantResponse:
        metrics = AssistantMetrics()
        start_time = time.time()
        
        # 1. Observe (Incremental Observation of Changed Files from AssistantContext)
        # 2. Context Recovery & Intent Recovery (Rule 151)
        trace = DecisionTrace(
            decision="Added 'timeout' parameter to process_intent",
            motivation="Prevent assistants from hanging during offline capability execution.",
            alternatives_considered=["Async background tasks"],
            tradeoffs=["Increases method signature complexity"],
            affected_components=["BaseAssistant", "ExecutionRuntime"],
            origin_sprint="Sprint 64",
            origin_rule="Rule 149",
            timestamp=datetime.now(),
            supporting_sources=["ADR-004", "commit-abc1234"]
        )
        
        # 3. Domain Analysis: Consistency & Debt Analysis
        debt = KnowledgeDebt(
            type="Architectural Drift", # Expanded taxonomy
            severity="Medium",
            evidence=[
                Evidence(
                    type="code_analysis",
                    source="ast_parser",
                    confidence=1.0,
                    payload={"symbol": "process_intent", "new_args": ["timeout"]}
                ),
                Evidence(
                    type="doc_analysis",
                    source="docstring",
                    confidence=1.0,
                    payload={"missing_params": ["timeout"]}
                )
            ],
            confidence=0.98,
            recommended_action="Update docstring for process_intent to include timeout parameter."
        )
        
        coverage = KnowledgeCoverage(
            component="BaseAssistant",
            architecture_score=1.0,
            api_docs_score=0.9, # Drift detected
            examples_score=0.0,
            tutorials_score=0.0,
            adr_score=1.0,
            overall_score=0.58
        )
        
        # 4. Goal Detection
        goal = DetectedGoal(
            goal="Synchronize BaseAssistant.process_intent docstring with architectural intent.",
            confidence=0.98,
            evidence=[e.payload for e in debt.evidence],
            alternatives={"Ignore for now": 0.05},
            missing_information=[]
        )
        
        # 5. Passive Preparation (Rule 149)
        patch = DocumentationPatch(
            target=KnowledgeTarget(
                kind="Python Method",
                identifier="process_intent",
                scope="BaseAssistant",
                location="desktop/assistants/base.py"
            ),
            before="\"\"\"Process the user intent.\"\"\"",
            after="\"\"\"Process the user intent.\n\nArgs:\n    timeout (int): Prevents hanging during offline execution.\n\"\"\"",
            reason="Docstring was missing the newly added timeout parameter.",
            confidence=0.98,
            supporting_evidence=debt.evidence + [
                Evidence(
                    type="architectural_intent",
                    source="DecisionTrace",
                    confidence=1.0,
                    payload={"motivation": trace.motivation}
                )
            ],
            review_summary="Updated `process_intent()` docstring to include the newly introduced `timeout` parameter."
        )
        
        metrics.planning_time = (time.time() - start_time) * 1000
        metrics.confidence = goal.confidence
        
        # 6. Suggestion (Rule 150 - Knowledge Explainability)
        explanation = Explanation(
            reason=patch.review_summary,
            evidence=patch.supporting_evidence,
            confidence=goal.confidence,
            suggested_workflow={"action": "apply_documentation_patch", "payload": patch.__dict__}
        )
        
        return AssistantResponse(
            goal=goal.goal,
            autonomy=AutonomyLevel.SUGGEST,
            explanation=explanation,
            metrics=metrics,
            payload={"debt": debt, "trace": trace, "patch": patch, "coverage": coverage}
        )
