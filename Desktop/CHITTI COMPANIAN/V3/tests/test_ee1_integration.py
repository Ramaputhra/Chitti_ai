import unittest
from desktop.orchestrator.state_machine import RuntimeStateMachine, RuntimeLifecycleState, InvalidStateTransitionException
from desktop.orchestrator.adapters import InputAdapter

class TestEE1Integration(unittest.TestCase):
    def test_state_machine_valid(self):
        sm = RuntimeStateMachine()
        sm.transition(RuntimeLifecycleState.INITIALIZING)
        self.assertEqual(sm.current_state, RuntimeLifecycleState.INITIALIZING)
        
    def test_state_machine_invalid(self):
        sm = RuntimeStateMachine()
        with self.assertRaises(InvalidStateTransitionException):
            sm.transition(RuntimeLifecycleState.RESPONDING)
            
    def test_input_adapter(self):
        adapter = InputAdapter()
        exp = adapter.translate("test", {}, {})
        # Updated to use new Experience API
        self.assertEqual(exp.goal, "test")

if __name__ == '__main__':
    unittest.main()
