import unittest
import os
from desktop.brain.consolidation.runtime import CognitiveArtifactRuntime
from desktop.brain.consolidation.engine import ConsolidationEngine
from desktop.brain.consolidation.models import LearnedRule

class TestSprint31DConsolidation(unittest.TestCase):
    
    def setUp(self):
        self.db_file = "test_cognitive_artifacts.db"
        self.runtime = CognitiveArtifactRuntime(db_path=self.db_file)
        self.engine = ConsolidationEngine(self.runtime)
        
    def tearDown(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

    def test_cpu_spike_transaction_abort(self):
        with self.assertRaises(Exception):
            self.engine.trigger_batch(cpu_load=80, episodes=[], graph_nodes=[], graph_edges=[])
        self.assertEqual(len(self.runtime.artifacts), 0)
        self.assertEqual(self.engine.checkpoint, 0)
        
    def test_memory_strength_curve(self):
        strength_0_days = self.engine.calculate_memory_strength(1.0, 0)
        strength_30_days = self.engine.calculate_memory_strength(1.0, 30)
        strength_60_days = self.engine.calculate_memory_strength(1.0, 60)
        
        self.assertEqual(strength_0_days, 1.0)
        self.assertLess(strength_30_days, strength_0_days)
        self.assertLess(strength_60_days, strength_30_days)
        
    def test_rule_superseding(self):
        rule1 = LearnedRule("r1", ["ep1"], "A", "Active", 1.0)
        self.engine.staging.append(rule1)
        self.runtime.commit(self.engine.staging)
        
        rule2 = LearnedRule("r2", ["ep2"], "B", "Active", 1.0)
        self.engine.supersede_rule("r1", rule2)
        
        self.assertEqual(self.runtime.artifacts["r1"].state, "Superseded")
        self.assertEqual(self.runtime.artifacts["r2"].state, "Active")

if __name__ == '__main__':
    unittest.main()
