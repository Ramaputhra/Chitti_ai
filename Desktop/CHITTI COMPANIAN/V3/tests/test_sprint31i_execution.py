import unittest
from desktop.brain.execution.engine import ExecutionEngine
from desktop.brain.execution.models import InvalidExecutionStateException

class MockStep:
    def __init__(self, sid, action):
        self.step_id = sid
        self.action_type = action
        self.payload = {}

class MockPlan:
    def __init__(self, pid, steps):
        self.plan_id = pid
        self.steps = steps
        self.plan_confidence = 1.0
        self.evidence_trace = "mock_trace"

class TestSprint31IExecution(unittest.TestCase):
    def setUp(self):
        self.engine = ExecutionEngine()
        
    def test_flawless_execution(self):
        plan = MockPlan("p1", [MockStep("s1", "OS_REGISTRY_EDIT")])
        session = self.engine.execute(plan)
        self.assertEqual(session.final_result.overall_status, "COMPLETED")
        self.assertEqual(len(session.final_result.step_results), 1)
        
    def test_retry_success(self):
        plan = MockPlan("p2", [MockStep("s1", "FAIL_ONCE")])
        session = self.engine.execute(plan)
        self.assertEqual(session.final_result.overall_status, "COMPLETED")
        
    def test_fatal_rollback(self):
        plan = MockPlan("p3", [MockStep("s1", "FAIL_ALWAYS")])
        session = self.engine.execute(plan)
        self.assertEqual(session.final_result.overall_status, "ROLLED_BACK")
        self.assertEqual(session.final_result.execution_confidence, 0.0)

if __name__ == '__main__':
    unittest.main()
