import unittest
from desktop.orchestrator.feedback_normalizer import FeedbackNormalizer, FeedbackClassification
from desktop.brain.execution.models import ExecutionStepResult

class TestEE4Integration(unittest.TestCase):
    def test_normalization(self):
        step = ExecutionStepResult(
            step_id="exec_1", intent="system.browser", status="FAILED", stdout="err", metadata={"rollback_performed": True}
        )
        norm = FeedbackNormalizer.normalize(step, "corr_1")
        self.assertEqual(norm["classification"], FeedbackClassification.ROLLBACK_SUCCESS)
        
if __name__ == '__main__':
    unittest.main()
