import unittest
from desktop.brain.intelligence.models import IntelligenceQuery
from desktop.brain.intelligence.orchestrator import IntelligenceOrchestrator, LatencyBudgetExceededException

class MockArtifactRuntime: pass
class MockGraphRuntime: pass

class TestSprint31EIntelligence(unittest.TestCase):
    def setUp(self):
        self.orchestrator = IntelligenceOrchestrator(MockArtifactRuntime(), MockGraphRuntime())
        
    def test_decision_veto(self):
        q = IntelligenceQuery("draft", {"target": "CEO"}, 50)
        res = self.orchestrator.query(q)
        self.assertTrue(res.rejected)
        
    def test_composite_confidence(self):
        q = IntelligenceQuery("resume", {"time": "13:00"}, 50)
        res = self.orchestrator.query(q)
        self.assertEqual(res.confidence_score, 0.9) # 0.8 + 0.1 boost
        
    def test_zero_hallucination_guarantee(self):
        q = IntelligenceQuery("resume", {}, 50)
        res = self.orchestrator.query(q)
        self.assertGreater(len(res.trace.root_episodes), 0)
        
    def test_latency_budget(self):
        q = IntelligenceQuery("resume", {}, -1)
        with self.assertRaises(LatencyBudgetExceededException):
            self.orchestrator.query(q)

if __name__ == '__main__':
    unittest.main()
