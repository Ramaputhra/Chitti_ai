import threading
from desktop.orchestrator.feedback_normalizer import FeedbackNormalizer
from desktop.orchestrator.feedback_governance import FeedbackGovernance

class ExecutionFeedbackCollector:
    def __init__(self, experience_builder, memory_compiler, knowledge_graph):
        self.experience_builder = experience_builder
        self.memory_compiler = memory_compiler
        self.knowledge_graph = knowledge_graph
        self.governance = FeedbackGovernance()
        self.cache = set()
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="FeedbackWorkerThread")
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def process_execution_result(self, execution_result, correlation_id):
        for step_result in getattr(execution_result, "step_results", []):
            exec_id = getattr(step_result, "step_id", "")
            if exec_id in self.cache:
                continue
            self.cache.add(exec_id)
            if len(self.cache) > 5000:
                self.cache.clear()
                
            normalized = FeedbackNormalizer.normalize(step_result, correlation_id)
            self.governance.submit(normalized)

    def _worker_loop(self):
        while self._running:
            feedback = self.governance.get_next()
            if feedback:
                try:
                    exp = self.experience_builder.build_system_feedback(feedback)
                    self.memory_compiler.compile(exp)
                    self.knowledge_graph.update_from_feedback(exp)
                except Exception:
                    pass
