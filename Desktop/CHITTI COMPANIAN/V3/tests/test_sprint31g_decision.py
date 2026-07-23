import unittest
from desktop.brain.decision.engine import DecisionEngine
from desktop.brain.decision.models import DecisionCandidate, DecisionBudgetExceededException, InvalidDecisionStateException

class MockConclusion:
    def __init__(self, conf):
        self.confidence = conf

class TestSprint31GDecision(unittest.TestCase):
    def setUp(self):
        self.engine = DecisionEngine()
        
    def test_session_generation(self):
        c1 = DecisionCandidate("1", "Test Intent", [MockConclusion(0.5)])
        session = self.engine.decide([c1])
        self.assertEqual(session.final_outcome.selected_intent, "Test Intent")
        
    def test_no_execution_mechanics(self):
        c1 = DecisionCandidate("1", "api_call to endpoint", [])
        with self.assertRaises(InvalidDecisionStateException):
            self.engine.decide([c1])
            
    def test_budget_exceeded(self):
        excessive = [DecisionCandidate(str(i), "intent", []) for i in range(25)]
        with self.assertRaises(DecisionBudgetExceededException):
            self.engine.decide(excessive)
            
    def test_risk_evaluation(self):
        c1 = DecisionCandidate("1", "delete file", [])
        session = self.engine.decide([c1])
        self.assertEqual(session.final_outcome.risk_level, "HIGH_REQUIRES_APPROVAL")

if __name__ == '__main__':
    unittest.main()
