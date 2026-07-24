import unittest
from desktop.orchestrator.context import PipelineContext
from desktop.models.experience import Experience
from datetime import datetime

class TestEE2Pipeline(unittest.TestCase):
    def test_pipeline_context_immutability(self):
        # Updated to use new Experience API
        exp = Experience(
            experience_id="123",
            artifact_id="art_123",
            artifact_type="Experience",
            capability_id="test",
            timestamp=None,
            summary="test",
            structured_result={},
            referenced_entities=[],
            supported_followup_actions=[],
            presentation_available=True,
            expiration_policy="",
            confidence=0.0,
            schema_version="1.0.0",
            experience_type="TEST",
            goal="test",
            outcome="ACTIVE",
            status="ACTIVE",
            start_time=datetime.now(),
            end_time=datetime.now(),
            decisions=[],
            participants=None,
            evidence=None,
            environment=None,
            scoring=None,
            continuation_candidate=False
        )
        ctx = PipelineContext(exp, "123")
        
        ctx.append_output("31A", "outputA")
        with self.assertRaises(ValueError):
            ctx.append_output("31A", "overwrite")
            
        self.assertEqual(ctx.get_output("31A"), "outputA")

if __name__ == '__main__':
    unittest.main()
