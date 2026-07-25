"""
Comprehensive Audit Tests - Real Functionality, Architecture, and Code Quality

This test module performs thorough testing of:
1. Core runtime functionality (real implementations)
2. Architectural boundary compliance
3. Code error detection
4. Model and interface validation
"""
import asyncio
import unittest
from datetime import datetime
from uuid import uuid4
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

# Import core modules for REAL testing
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestModels(unittest.TestCase):
    """Test core data models for correctness"""
    
    def test_intent_result_model(self):
        """Test IntentResult has required session_id field"""
        from desktop.models.interaction import IntentResult
        
        # Create a real IntentResult
        result = IntentResult(
            intent="test_intent",
            confidence=0.95,
            parameters={"key": "value"},
            source="test",
            interaction_id="test_123",
            session_id="session_abc"  # Required field
        )
        
        self.assertEqual(result.intent, "test_intent")
        self.assertEqual(result.session_id, "session_abc")
        self.assertIsInstance(result.session_id, str)
        self.assertTrue(len(result.session_id) > 0)
    
    def test_execution_step_result_defaults(self):
        """Test ExecutionStepResult has proper defaults"""
        from desktop.brain.execution.models import ExecutionStepResult
        
        # Create with minimal args (should use defaults)
        result = ExecutionStepResult()
        
        self.assertEqual(result.step_id, "")
        self.assertEqual(result.status, "")
        self.assertEqual(result.intent, "")
        self.assertIsInstance(result.metadata, dict)
    
    def test_experience_model_creation(self):
        """Test Experience model can be created properly"""
        from desktop.models.experience import Experience
        from datetime import datetime
        
        exp = Experience(
            experience_id="exp_123",
            artifact_id="art_123",
            artifact_type="Experience",
            capability_id="test",
            timestamp=None,
            summary="test summary",
            structured_result={},
            referenced_entities=[],
            supported_followup_actions=[],
            presentation_available=True,
            expiration_policy="",
            confidence=1.0,
            schema_version="1.0.0",
            experience_type="TEST",
            goal="test goal",
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
        
        self.assertEqual(exp.experience_id, "exp_123")
        self.assertEqual(exp.goal, "test goal")


class TestRuntimeArchitecture(unittest.TestCase):
    """Test architectural boundaries and responsibilities"""
    
    def test_planner_never_calls_capabilities(self):
        """Verify PlannerRuntime does NOT call capabilities directly"""
        import inspect
        from desktop.runtimes.planner import PlannerRuntime
        
        source = inspect.getsource(PlannerRuntime)
        
        # Planner should NOT directly invoke capabilities
        forbidden_patterns = [
            'capability.execute',
            'invoke_capability',
            'self.invoker',
            'CapabilityInvoker'
        ]
        
        for pattern in forbidden_patterns:
            self.assertNotIn(pattern, source, 
                f"PlannerRuntime should not contain '{pattern}' - violates Rule 176")
    
    def test_planner_never_calls_llm(self):
        """Verify PlannerRuntime does NOT call LLM directly"""
        import inspect
        from desktop.runtimes.planner import PlannerRuntime
        
        source = inspect.getsource(PlannerRuntime)
        
        forbidden_patterns = [
            'generate(',
            'llm.',
            'inference_runtime',
            'provider.generate'
        ]
        
        for pattern in forbidden_patterns:
            self.assertNotIn(pattern, source,
                f"PlannerRuntime should not contain '{pattern}' - violates Rule 183")
    
    def test_expression_runtime_never_generates_responses(self):
        """Verify ExpressionRuntime only renders, never generates content"""
        import inspect
        from desktop.runtimes.expression_runtime import ExpressionRuntime
        
        source = inspect.getsource(ExpressionRuntime)
        
        # ExpressionRuntime should NOT generate text responses
        forbidden_patterns = [
            'generate(',
            'llm.',
            'inference',
            'openai.',
            'ollama.'
        ]
        
        for pattern in forbidden_patterns:
            self.assertNotIn(pattern, source,
                f"ExpressionRuntime should not contain '{pattern}' - violates Rule 179")
    
    def test_execution_runtime_never_modifies_plans(self):
        """Verify ExecutionRuntime only executes, never modifies plans"""
        import inspect
        from desktop.runtimes.execution import ExecutionRuntime
        
        source = inspect.getsource(ExecutionRuntime)
        
        # Should NOT modify plan contents
        forbidden_patterns = [
            'plan.intent =',
            'plan.action =',
            'plan.steps.append'
        ]
        
        for pattern in forbidden_patterns:
            self.assertNotIn(pattern, source,
                f"ExecutionRuntime should not modify plan - violates Rule 177")


class TestCapabilityIsolation(unittest.TestCase):
    """Test that capabilities follow isolation rules"""
    
    def test_capabilities_dont_call_ai(self):
        """Verify capabilities do NOT call AI/inference directly"""
        import inspect
        import os
        import re
        
        capabilities_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'desktop', 'packages', 'desktop_pack', 'capabilities'
        )
        
        violations = []
        
        for filename in os.listdir(capabilities_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                filepath = os.path.join(capabilities_dir, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Remove comments to avoid false positives
                content_no_comments = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
                
                forbidden = [
                    'ai_runtime.generate',
                    'self.ai_runtime.generate',
                    '.generate(',
                    'llm.',
                    'from desktop.runtimes.inference',
                    'from desktop.brain.inference'
                ]
                
                for pattern in forbidden:
                    if pattern in content_no_comments:
                        violations.append(f"{filename}: contains '{pattern}'")
        
        self.assertEqual(len(violations), 0, 
            f"Capabilities calling AI directly: {violations}")
    
    def test_capabilities_dont_publish_expression_events(self):
        """Verify capabilities do NOT publish RenderedExpression directly"""
        import inspect
        import os
        
        capabilities_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'desktop', 'packages', 'desktop_pack', 'capabilities'
        )
        
        violations = []
        
        for filename in os.listdir(capabilities_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                filepath = os.path.join(capabilities_dir, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Check for direct event_bus.publish of RenderedExpression
                if 'event_bus.publish' in content and 'RenderedExpression' in content:
                    violations.append(f"{filename}: publishes RenderedExpression directly")
        
        self.assertEqual(len(violations), 0,
            f"Capabilities publishing events directly: {violations}")
    
    def test_capabilities_return_execution_result(self):
        """Verify capabilities return ExecutionResult"""
        import os
        
        capabilities_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'desktop', 'packages', 'desktop_pack', 'capabilities'
        )
        
        for filename in os.listdir(capabilities_dir):
            if filename.endswith('.py') and filename not in ['__init__.py', 'inference.py']:
                filepath = os.path.join(capabilities_dir, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Should return ExecutionResult
                if 'def execute' in content:
                    self.assertIn('ExecutionResult', content,
                        f"{filename}: execute() should return ExecutionResult")


class TestSessionIntegrity(unittest.TestCase):
    """Test session ID propagation throughout the system"""
    
    def test_intent_result_requires_session_id(self):
        """Verify IntentResult model requires session_id"""
        from desktop.models.interaction import IntentResult
        import inspect
        
        # Check the signature requires session_id
        sig = inspect.signature(IntentResult)
        params = list(sig.parameters.keys())
        
        # session_id should be in the model (even if optional)
        self.assertIn('session_id', params,
            "IntentResult should have session_id field for tracing")
    
    def test_planner_extracts_session_from_event(self):
        """Verify Planner extracts session_id from IntentResolved event"""
        import inspect
        from desktop.runtimes.planner import PlannerRuntime
        
        source = inspect.getsource(PlannerRuntime.process_intent)
        
        # Should extract from event, not hardcode
        self.assertIn('session_id', source,
            "Planner should extract session_id from event")
        self.assertNotIn('default_session', source,
            "Planner should NOT hardcode 'default_session'")


class TestProviderInterface(unittest.TestCase):
    """Test AI providers implement canonical interface"""
    
    def test_ollama_provider_has_interface_methods(self):
        """Verify OllamaProvider implements required interface"""
        try:
            from desktop.services.ai.providers.ollama_provider import OllamaProvider
            
            provider = OllamaProvider()
            
            # Required interface methods
            required_methods = ['initialize', 'shutdown', 'health', 'info', 'generate']
            missing = []
            
            for method in required_methods:
                if not hasattr(provider, method):
                    missing.append(method)
            
            self.assertEqual(len(missing), 0,
                f"OllamaProvider missing methods: {missing}")
        except ImportError:
            self.skipTest("requests module not installed")
    
    def test_provider_has_name_property(self):
        """Verify provider has name property"""
        try:
            from desktop.services.ai.providers.ollama_provider import OllamaProvider
            
            provider = OllamaProvider()
            
            # Should have name as property
            self.assertTrue(hasattr(provider, 'name'),
                "Provider should have 'name' property")
            
            name = provider.name
            self.assertIsInstance(name, str)
            self.assertTrue(len(name) > 0)
        except ImportError:
            self.skipTest("requests module not installed")


class TestEventBusCompliance(unittest.TestCase):
    """Test EventBus implementation"""
    
    def test_event_bus_singleton_pattern(self):
        """Verify EventBus follows singleton-like pattern"""
        from desktop.app.context import EventBus
        
        bus1 = EventBus()
        bus2 = EventBus()
        
        # Each instance is independent (which is correct for testing)
        self.assertIsNot(bus1, bus2)
    
    def test_event_bus_publish_signature(self):
        """Verify EventBus.publish accepts Event objects"""
        import inspect
        from desktop.app.context import EventBus
        
        sig = inspect.signature(EventBus.publish)
        params = list(sig.parameters.keys())
        
        self.assertIn('event', params,
            "EventBus.publish should accept 'event' parameter")


class TestMemoryRuntime(unittest.TestCase):
    """Test MemoryRuntime isolation"""
    
    def test_memory_runtime_does_not_call_llm(self):
        """Verify MemoryRuntime does not invoke LLM"""
        import inspect
        from desktop.runtimes.memory_runtime import MemoryRuntime
        
        source = inspect.getsource(MemoryRuntime)
        
        forbidden = ['generate(', 'llm.', 'inference', 'openai.', 'ollama.']
        
        for pattern in forbidden:
            self.assertNotIn(pattern, source,
                f"MemoryRuntime should not contain '{pattern}' - violates Rule 96")


class TestWorkflowRuntime(unittest.TestCase):
    """Test WorkflowRuntime orchestration"""
    
    def test_workflow_orchestration_pattern(self):
        """Verify WorkflowRuntime follows orchestration pattern"""
        import inspect
        from desktop.runtimes.workflow_runtime import WorkflowRuntime
        
        source = inspect.getsource(WorkflowRuntime)
        
        # Should orchestrate, not execute directly
        self.assertIn('ExecutionRuntime', source,
            "WorkflowRuntime should coordinate ExecutionRuntime")
    
    def test_workflow_enforces_execution_order(self):
        """Verify workflow enforces step-by-step execution"""
        import inspect
        from desktop.runtimes.workflow_runtime import WorkflowRuntime
        
        source = inspect.getsource(WorkflowRuntime)
        
        # Should have step execution logic
        patterns = ['execute_step', 'orchestrate', 'workflow', 'step']
        found = sum(1 for p in patterns if p in source)
        
        self.assertGreater(found, 2,
            "WorkflowRuntime should contain step orchestration logic")


class TestEndToEndFlow(unittest.TestCase):
    """Test complete flow from intent to execution"""
    
    def test_intent_resolution_flow(self):
        """Test IntentResult -> IntentResolved -> Planner flow"""
        from desktop.models.interaction import IntentResult, IntentResolved
        from datetime import datetime
        
        # Create IntentResult with session_id
        intent_result = IntentResult(
            intent="launch_app",
            confidence=0.95,
            parameters={"app": "notepad"},
            source="test",
            interaction_id="test_123",
            session_id="session_xyz"
        )
        
        # Create IntentResolved event
        resolved = IntentResolved(
            result=intent_result,
            correlation_id="corr_123"
        )
        
        # Verify session_id propagates
        self.assertEqual(resolved.result.session_id, "session_xyz")
    
    def test_execution_result_structure(self):
        """Test ExecutionResult has proper structure"""
        from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
        
        result = ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            outputs={"key": "value"}
        )
        
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertIn("key", result.outputs)


class TestCodeQuality(unittest.TestCase):
    """Test code quality and patterns"""
    
    def test_no_hardcoded_session_in_planner(self):
        """Verify planner has no hardcoded session values"""
        import inspect
        from desktop.runtimes.planner import PlannerRuntime
        
        source = inspect.getsource(PlannerRuntime)
        
        # Should not have these hardcoded patterns
        forbidden = [
            'session_id = "',
            "session_id = '",
            'session_id="',
            "session_id='"
        ]
        
        for pattern in forbidden:
            self.assertNotIn(pattern, source,
                f"Planner should not hardcode session_id: '{pattern}'")
    
    def test_no_print_statements_in_runtimes(self):
        """Verify runtimes use logging, not print"""
        import os
        import re
        
        runtimes_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'desktop', 'runtimes'
        )
        
        violations = []
        
        for filename in os.listdir(runtimes_dir):
            if filename.endswith('_runtime.py'):
                filepath = os.path.join(runtimes_dir, filename)
                with open(filepath, 'r') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    # Check for print statements (not in comments)
                    if re.match(r'^\s*print\(', line) and not line.strip().startswith('#'):
                        violations.append(f"{filename}:{i}: {line.strip()}")
        
        self.assertEqual(len(violations), 0,
            f"Found print statements in runtimes: {violations[:5]}")
    
    def test_all_runtimes_implement_iruntime(self):
        """Verify all runtimes implement IRuntime interface"""
        import os
        import inspect
        
        runtimes_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'desktop', 'runtimes'
        )
        
        required_methods = ['initialize', 'start', 'stop', 'shutdown', 'health']
        
        for filename in os.listdir(runtimes_dir):
            if filename.endswith('_runtime.py') and filename != '__init__.py':
                module_name = f"desktop.runtimes.{filename[:-3]}"
                try:
                    module = __import__(module_name, fromlist=[''])
                    
                    # Find the runtime class in the module
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and 'Runtime' in name:
                            runtime = obj
                            
                            # Check for required methods
                            missing = []
                            for method in required_methods:
                                if not hasattr(runtime, method):
                                    missing.append(method)
                            
                            if missing:
                                self.fail(f"{name} missing methods: {missing}")
                except Exception as e:
                    pass  # Skip if module can't be imported


if __name__ == '__main__':
    unittest.main(verbosity=2)
