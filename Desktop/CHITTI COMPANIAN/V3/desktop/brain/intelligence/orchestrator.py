import time
from desktop.brain.intelligence.models import IntelligenceResult, ExplainabilityTrace, IntelligenceQuery
from desktop.brain.intelligence.services import ContextIntelligenceService, ResumeIntelligenceService, RecallIntelligenceService
from desktop.brain.intelligence.decision import DecisionIntelligenceService, RecommendationIntelligenceService
from desktop.brain.intelligence.explainability import ExplainabilityService

class LatencyBudgetExceededException(Exception): pass

class IntelligenceOrchestrator:
    def __init__(self, artifact_runtime, graph_runtime):
        self.artifact_runtime = artifact_runtime
        self.graph_runtime = graph_runtime
        
        self.decision = DecisionIntelligenceService()
        self.context = ContextIntelligenceService()
        self.resume = ResumeIntelligenceService()
        self.recall = RecallIntelligenceService()
        self.recommend = RecommendationIntelligenceService()
        self.explain = ExplainabilityService()
        
    def query(self, query: IntelligenceQuery) -> IntelligenceResult:
        start = time.time()
        
        # 1. Decision Service holds Absolute Veto (Conflict Resolution)
        dec_res = self.decision.evaluate(query, self.artifact_runtime, self.graph_runtime)
        if dec_res.rejected:
            return self._finalize_result(dec_res, start, query.max_latency_ms)
            
        # 2. Fan-out execution to appropriate service (Resume for this mock)
        res_res = self.resume.evaluate(query, self.artifact_runtime, self.graph_runtime)
        
        # 3. Composite Confidence Computation
        base_conf = res_res.confidence_score
        boost = 0.10 # Deterministic topological boost applied
        comp_conf = min(1.0, base_conf + boost)
        
        # 4. Generate the final Explainability Trace
        final_trace = ExplainabilityTrace(
            contributing_artifacts=res_res.trace.contributing_artifacts,
            topological_paths=res_res.trace.topological_paths,
            root_episodes=res_res.trace.root_episodes,
            conflict_overrides=[],
            modifiers=[f"Topological Boost: +{boost}"]
        )
        
        final_res = IntelligenceResult(res_res.primary_insight, comp_conf, final_trace)
        return self._finalize_result(final_res, start, query.max_latency_ms)
        
    def _finalize_result(self, result: IntelligenceResult, start_time: float, max_latency_ms: int):
        elapsed = (time.time() - start_time) * 1000
        if elapsed > max_latency_ms:
            raise LatencyBudgetExceededException(f"Query took {elapsed:.2f}ms, exceeding budget of {max_latency_ms}ms")
        return result
