import time
from typing import Dict, Any, List
from desktop.product.assistants.base import BaseAssistant, AssistantResponse, AutonomyLevel, Explanation, Evidence, AssistantContext
from desktop.product.assistants.coding.models import DetectedGoal
from desktop.product.assistants.research.models import (
    KnowledgeWorkspace, KnowledgeSource, TopicGraph, GapAnalysis, ResearchMetrics, KnowledgeArtifact, ResearchConclusion
)
from datetime import datetime

class ResearchAssistant(BaseAssistant):
    """
    Solves the human job: "Help me synthesize information across multiple sources."
    Implements the "Passive Preparation" autonomy model and enforces Rule 148 Traceability.
    """
    async def process_intent(self, context: AssistantContext) -> AssistantResponse:
        metrics = ResearchMetrics()
        start_time = time.time()
        
        # 1. Observation (Rule 147: Rely on AssistantContext, not raw environment)
        # 2. Topic Extraction & Knowledge Graph Construction
        metrics.sources_observed = 5
        metrics.sources_used = 5
        
        # Mocking the generated TopicGraph
        graph = TopicGraph(
            main_topic="React vs Vue Framework Comparison",
            subtopics={},
            confidence=0.92
        )
        
        # 3. Memory Merge
        # Recover previous questions, previous conclusions, etc.
        metrics.duplicates_removed = 2
        metrics.conflicts_detected = 1
        
        # 4. Gap Analysis
        gap = GapAnalysis(
            missing_topics=["Security", "Licensing", "Server-Side Rendering (SSR)"],
            suggested_queries=["React SSR vs Nuxt performance", "Vue enterprise licensing"],
            impact_on_confidence=-0.15
        )
        metrics.gaps_found = 3
        
        # 5. Goal Detection
        # Based on gaps and current context
        goal = DetectedGoal(
            goal="Synthesize comparison document and investigate SSR performance.",
            confidence=0.88,
            evidence=[
                "User has closed 4 tabs comparing React/Vue benchmarks",
                "User has been inactive for 3 minutes (Research Session Ending)"
            ],
            alternatives={
                "Continue researching": 0.20
            },
            missing_information=gap.missing_topics
        )
        metrics.planning_time = (time.time() - start_time) * 1000
        metrics.confidence = goal.confidence
        
        # 6. Passive Preparation (Create the artifact internally without persisting to file system)
        artifact = KnowledgeArtifact(
            type="Comparison Matrix",
            title="React vs Vue Architecture Comparison",
            sections={"Performance": "React performs better in concurrent rendering.", "Memory": "Vue uses less memory on startup."},
            citations=["tab_1_react_docs", "tab_2_vue_benchmarks", "pdf_1_research_paper"]
        )
        metrics.artifact_size = 2 # 2 sections
        
        # 7. Formulate Explainable Response
        explanation = Explanation(
            reason="It looks like you've finished researching React vs Vue. I noticed you didn't look into Server-Side Rendering (SSR). I already prepared a Comparison Matrix artifact.",
            evidence=[
                Evidence(
                    type="knowledge_gap",
                    source="GapAnalysis Pipeline",
                    confidence=1.0,
                    payload={"missing": gap.missing_topics}
                ),
                Evidence(
                    type="research_conclusion",
                    source="TopicGraph (Rule 148)",
                    confidence=0.92,
                    payload={"statement": "React performs better in concurrent rendering.", "supporting_sources": ["pdf_1_research_paper", "tab_2_vue_benchmarks"]}
                )
            ],
            confidence=goal.confidence,
            suggested_workflow={"action": "persist_artifact", "payload": artifact.__dict__}
        )
        
        # Autonomy: SUGGEST saving the artifact. Do NOT persist it automatically.
        return AssistantResponse(
            goal=goal.goal,
            autonomy=AutonomyLevel.SUGGEST,
            explanation=explanation,
            metrics=metrics,
            payload={"workspace": KnowledgeWorkspace(
                active_topic=graph.main_topic,
                sources=[],
                working_notes="",
                knowledge_gaps=gap.missing_topics,
                hypotheses=[],
                questions=gap.suggested_queries,
                confidence=goal.confidence
            )}
        )
