import unittest
from desktop.orchestrator.capability_manifest import CapabilityManifest, CapabilityLifecycleState
from desktop.orchestrator.capability_binder import CompatibilityLayer

def dummy_v1():
    return "success"

class TestEE3Integration(unittest.TestCase):
    def test_lifecycle(self):
        m = CapabilityManifest("test", [], "1.0", [], {}, {}, False, 1000, False)
        layer = CompatibilityLayer(m, dummy_v1)
        self.assertEqual(layer.state, CapabilityLifecycleState.REGISTERED)
        layer.initialize()
        self.assertEqual(layer.state, CapabilityLifecycleState.READY)
        
    def test_provenance(self):
        m = CapabilityManifest("test", [], "1.0", [], {}, {}, False, 1000, False)
        layer = CompatibilityLayer(m, dummy_v1)
        layer.initialize()
        res = layer.execute({}, 1.0)
        self.assertEqual(res.metadata["capability_id"], "test")

if __name__ == '__main__':
    unittest.main()
