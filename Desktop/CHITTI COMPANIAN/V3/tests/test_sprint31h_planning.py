import unittest
from desktop.brain.planning.engine import PlanningEngine
from desktop.brain.planning.models import InvalidPlanningStateException

class MockDecision:
    def __init__(self, intent, conf):
        self.selected_intent = intent
        self.decision_confidence = conf
        self.outcome_id = "mock"

class TestSprint31HPlanning(unittest.TestCase):
    def setUp(self):
        self.engine = PlanningEngine()
        
    def test_session_compilation(self):
        d1 = MockDecision("mute notifications", 1.0)
        session = self.engine.plan(d1)
        self.assertEqual(len(session.final_plan.steps), 2)
        self.assertTrue(session.final_plan.is_executable)
        
    def test_prerequisite_failure(self):
        d1 = MockDecision("upload crash logs", 1.0)
        session = self.engine.plan(d1)
        self.assertFalse(session.final_plan.is_executable)
        self.assertEqual(session.final_plan.plan_confidence, 0.0)
        
    def test_circular_dependency(self):
        d1 = MockDecision("circular test", 1.0)
        with self.assertRaises(InvalidPlanningStateException):
            self.engine.plan(d1)

if __name__ == '__main__':
    unittest.main()
