import unittest
import uuid
from desktop.brain.graph.builder import GraphBuilder
from desktop.brain.graph.validator import GraphValidator
from desktop.brain.graph.runtime import GraphRuntime
from desktop.brain.graph.query import GraphQuery

class TestSprint31CGraph(unittest.TestCase):
    
    def test_end_to_end_graph_pipeline(self):
        episode = {
            "episode_id": str(uuid.uuid4()),
            "content": "test episode",
            "metadata": {}
        }
        
        builder = GraphBuilder()
        delta = builder.build_delta(episode)
        self.assertIsNotNone(delta)
        
        validator = GraphValidator()
        self.assertTrue(validator.validate(delta))
        
        runtime = GraphRuntime()
        runtime.apply_delta(delta)
        
        self.assertEqual(len(runtime.nodes), 1)
        
        query = GraphQuery(runtime)
        res = query.find_neighborhood("n_arch")
        self.assertEqual(len(res["nodes"]), 1)

if __name__ == '__main__':
    unittest.main()
