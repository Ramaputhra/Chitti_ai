import unittest
from desktop.brain.reasoning.engine import ReasoningEngine
from desktop.brain.reasoning.models import ReasoningBudgetExceededException

class MockIntelligenceResult:
    def __init__(self, conf, rejected=False):
        self.confidence_score = conf
        self.rejected = rejected

class TestSprint31FReasoning(unittest.TestCase):
    def setUp(self):
        self.engine = ReasoningEngine()
        
    def test_session_generation(self):
        session = self.engine.reason("test", [MockIntelligenceResult(0.8)])
        self.assertEqual(session.final_conclusion.assertion, "Action Approved")
        
    def test_conflict_resolution(self):
        session = self.engine.reason("test", [MockIntelligenceResult(0.8, False), MockIntelligenceResult(1.0, True)])
        self.assertEqual(session.final_conclusion.assertion, "Action Rejected")
        
    def test_budget_exceeded(self):
        with self.assertRaises(ReasoningBudgetExceededException):
            self.engine.reason("test", [], budget_depth=4)
            
    def test_confidence_propagation(self):
        session = self.engine.reason("test", [MockIntelligenceResult(0.8, False)])
        self.assertEqual(session.final_conclusion.confidence, 0.75) # 0.8 base - 0.05 decay

if __name__ == '__main__':
    unittest.main()
