import time
from desktop.orchestrator.state_machine import PipelineEventBus
from desktop.orchestrator.context import PipelineContext
from desktop.orchestrator.metrics import RuntimeMetricsLogger
from desktop.models.experience import Experience
from desktop.brain.execution.models import ExecutionResult, ExecutionTrace

class PipelineTimeoutException(Exception):
    pass

class CognitivePipeline:
    def __init__(self, 
                 event_bus: PipelineEventBus,
                 experience_intelligence, # 31A
                 cognitive_memory,        # 31B
                 knowledge_graph,         # 31C
                 consolidation_engine,    # 31D
                 intelligence_services,   # 31E
                 reasoning_foundation,    # 31F
                 decision_framework,      # 31G
                 planning_foundation,     # 31H
                 execution_runtime        # 31I
                 ):
        self.event_bus = event_bus
        self.metrics = RuntimeMetricsLogger()
        self.sprint_31a = experience_intelligence
        self.sprint_31b = cognitive_memory
        self.sprint_31c = knowledge_graph
        self.sprint_31d = consolidation_engine
        self.sprint_31e = intelligence_services
        self.sprint_31f = reasoning_foundation
        self.sprint_31g = decision_framework
        self.sprint_31h = planning_foundation
        self.sprint_31i = execution_runtime
        
        self.max_total_duration_ms = 60000
        self.max_stage_duration_ms = 15000
        
        from desktop.orchestrator.feedback_collector import ExecutionFeedbackCollector
        self.feedback_collector = ExecutionFeedbackCollector(
            self.sprint_31a, 
            self.sprint_31b, 
            self.sprint_31c
        )
        self.feedback_collector.start()

    def _enforce_budget(self, start_time: float):
        if (time.time() - start_time) * 1000 > self.max_total_duration_ms:
            raise PipelineTimeoutException("Pipeline Budget Exceeded: Total Duration > 60000ms")

    def _execute_stage(self, stage_name: str, context: PipelineContext, func, input_data, event_name: str):
        if context.is_cancelled:
            return False
            
        self._enforce_budget(context.start_time)
        self.metrics.start_stage(stage_name, context.correlation_id)
        
        try:
            stage_start = time.time()
            output = func(input_data)
            if (time.time() - stage_start) * 1000 > self.max_stage_duration_ms:
                raise PipelineTimeoutException(f"Stage Budget Exceeded for {stage_name}")
                
            context.append_output(stage_name, output)
            self.metrics.end_stage(stage_name, context.correlation_id, "SUCCESS")
            self.event_bus.publish(event_name, {"correlation_id": context.correlation_id})
            return True
        except Exception as e:
            self.metrics.end_stage(stage_name, context.correlation_id, "FAILURE")
            raise

    def process(self, experience: Experience) -> ExecutionResult:
        correlation_id = experience.experience_id
        context = PipelineContext(experience, correlation_id)
        
        self.event_bus.publish("PipelineStarted", {"correlation_id": correlation_id})
        
        try:
            # 31A
            self._execute_stage("31A", context, self.sprint_31a.process, context.root_experience, "ExperienceCreated")
            # 31B
            self._execute_stage("31B", context, self.sprint_31b.store, context.get_output("31A"), "MemoryStored")
            # 31C
            self._execute_stage("31C", context, self.sprint_31c.update, context.get_output("31B"), "GraphUpdated")
            # 31D
            self._execute_stage("31D", context, self.sprint_31d.evaluate, context.get_output("31C"), "ConsolidationCompleted")
            # 31E
            self._execute_stage("31E", context, self.sprint_31e.analyze, (context.get_output("31D"), context.root_experience), "IntelligenceAnalyzed")
            # 31F
            self._execute_stage("31F", context, self.sprint_31f.reason, context.get_output("31E"), "ReasoningCompleted")
            # 31G
            self._execute_stage("31G", context, self.sprint_31g.decide, context.get_output("31F"), "DecisionCompleted")
            # 31H
            self._execute_stage("31H", context, self.sprint_31h.compile, context.get_output("31G"), "PlanningCompleted")
            
            self.event_bus.publish("ExecutionStarted", {"correlation_id": correlation_id})
            
            # 31I
            self._execute_stage("31I", context, self.sprint_31i.execute, context.get_output("31H"), "ExecutionCompleted")
            
            res = context.get_output("31I")
            
            # EE4 Integration
            self.feedback_collector.process_execution_result(res, correlation_id)
            
            return res
            
        except Exception as e:
            self.event_bus.publish("PipelineError", {"correlation_id": correlation_id, "error": str(e)})
            return ExecutionResult(
                result_id="err_" + correlation_id,
                overall_status="FAILED",
                step_results=[],
                execution_confidence=0.0,
                evidence_trace=ExecutionTrace(execution_plan_id="N/A", compilation_trace=None)
            )
