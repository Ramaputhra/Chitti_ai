from desktop.brain.intelligence.models import IntelligenceResult, ExplainabilityTrace, IntelligenceQuery

class ContextIntelligenceService:
    def evaluate(self, query: IntelligenceQuery, artifacts, graph) -> IntelligenceResult:
        return IntelligenceResult("Context applied", 0.6, ExplainabilityTrace())

class ResumeIntelligenceService:
    def evaluate(self, query: IntelligenceQuery, artifacts, graph) -> IntelligenceResult:
        trace = ExplainabilityTrace(contributing_artifacts=["Habit_442"], root_episodes=["ep_014"])
        return IntelligenceResult("Resume Notion Workspace", 0.8, trace)

class RecallIntelligenceService:
    def evaluate(self, query: IntelligenceQuery, artifacts, graph) -> IntelligenceResult:
        trace = ExplainabilityTrace(contributing_artifacts=["Mem_91"], root_episodes=["ep_089"])
        return IntelligenceResult("Project X Architecture Details", 0.9, trace)
