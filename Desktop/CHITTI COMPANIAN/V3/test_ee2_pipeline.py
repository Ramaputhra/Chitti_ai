import unittest
from desktop.orchestrator.context import PipelineContext
from desktop.models.experience import Experience

class TestEE2Pipeline(unittest.TestCase):
    def test_pipeline_context_immutability(self):
        exp = Experience("123", "test", {}, 0.0)
        ctx = PipelineContext(exp, "123")
        
        ctx.append_output("31A", "outputA")
        with self.assertRaises(ValueError):
            ctx.append_output("31A", "overwrite")
            
        self.assertEqual(ctx.get_output("31A"), "outputA")

if __name__ == '__main__':
    unittest.main()
