"""
Functionality Audit Tests - Real Code Execution Tests

This test module tests actual functionality of:
1. Model instantiation and behavior
2. Runtime lifecycle methods
3. Event bus functionality
4. Service registry functionality
5. Adapter transformations
"""
import unittest
import asyncio
import tempfile
import os
from datetime import datetime
from uuid import uuid4
from dataclasses import dataclass

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestModelInstantiation(unittest.TestCase):
    """Test all models can be instantiated correctly"""
    
    def test_event_models(self):
        """Test event models work correctly"""
        from desktop.models.events import PlanCreated
        
        # Create PlanCreated
        plan_event = PlanCreated(
            timestamp=datetime.now(),
            source="test",
            correlation_id="corr_123",
            domain="Cognition",
            action="PlanCreated",
            payload={"plan_id": "plan_123"}
        )
        self.assertEqual(plan_event.action, "PlanCreated")
        self.assertEqual(plan_event.correlation_id, "corr_123")
    
    def test_interaction_models(self):
        """Test interaction models"""
        from desktop.models.interaction import InteractionEnvelope, IntentResult, IntentResolved
        
        # Create InteractionEnvelope
        envelope = InteractionEnvelope(
            id="env_123",
            correlation_id="corr_123",
            timestamp=datetime.now(),
            origin="voice",
            transport="local",
            session_id="session_xyz",
            payload="Hello"
        )
        self.assertEqual(envelope.session_id, "session_xyz")
        
        # Create IntentResult
        result = IntentResult(
            intent="launch_app",
            confidence=0.95,
            parameters={"app": "notepad"},
            source="voice",
            interaction_id="env_123",
            session_id="session_xyz"
        )
        self.assertEqual(result.intent, "launch_app")
        self.assertEqual(result.session_id, "session_xyz")
    
    def test_execution_models(self):
        """Test execution models"""
        from desktop.models.execution import ExecutionStep
        from desktop.runtimes.capability.results import ExecutionStatus
        
        step = ExecutionStep(
            step_id="step_1",
            capability_name="launch_app",
            status=ExecutionStatus.SUCCESS,
            start_time=datetime.now().timestamp(),
            end_time=0
        )
        self.assertEqual(step.capability_name, "launch_app")
    
    def test_presentation_models(self):
        """Test presentation models"""
        from desktop.models.presentation import AvatarStateChanged, AvatarState
        
        avatar_change = AvatarStateChanged(state=AvatarState.SPEAKING)
        self.assertEqual(avatar_change.state, AvatarState.SPEAKING)


class TestRuntimeLifecycle(unittest.TestCase):
    """Test runtime lifecycle methods"""
    
    def test_planner_runtime_lifecycle(self):
        """Test PlannerRuntime lifecycle methods"""
        from desktop.runtimes.planner import PlannerRuntime
        from desktop.models.lifecycle import HealthState
        from desktop.app.planner_contracts import IPlannerStrategy
        
        # Create mock strategy
        class MockStrategy(IPlannerStrategy):
            @property
            def version(self): return "1.0.0"
            
            def parse_intent(self, event, snapshot): return {}
            def formulate_decision(self, intent, snapshot): return {}
            def create_plan(self, decision, event, session_id): return None
        
        runtime = PlannerRuntime(strategy=MockStrategy())
        
        # Test lifecycle methods exist
        self.assertTrue(hasattr(runtime, 'initialize'))
        self.assertTrue(hasattr(runtime, 'start'))
        self.assertTrue(hasattr(runtime, 'stop'))
        self.assertTrue(hasattr(runtime, 'shutdown'))
        self.assertTrue(hasattr(runtime, 'health'))
        
        # Test health check
        health = runtime.health()
        self.assertEqual(health, HealthState.HEALTHY)
    
    def test_execution_runtime_lifecycle(self):
        """Test ExecutionRuntime lifecycle methods"""
        from desktop.runtimes.execution import ExecutionRuntime
        from desktop.runtimes.capability.registry import CapabilityRegistry
        from desktop.models.lifecycle import HealthState
        
        registry = CapabilityRegistry()
        runtime = ExecutionRuntime(registry=registry)
        
        # Test lifecycle methods exist
        self.assertTrue(hasattr(runtime, 'initialize'))
        self.assertTrue(hasattr(runtime, 'start'))
        self.assertTrue(hasattr(runtime, 'stop'))
        self.assertTrue(hasattr(runtime, 'shutdown'))
        self.assertTrue(hasattr(runtime, 'health'))
        
        # Test health check
        health = runtime.health()
        self.assertEqual(health, HealthState.HEALTHY)
    
    def test_expression_runtime_lifecycle(self):
        """Test ExpressionRuntime lifecycle methods"""
        from desktop.runtimes.expression_runtime import ExpressionRuntime
        from desktop.app.presentation_contracts import IExpressionRenderer
        from desktop.models.lifecycle import HealthState
        
        # Create mock renderer
        class MockRenderer(IExpressionRenderer):
            def get_format_name(self): return "text"
            def render(self, request): return "rendered"
        
        runtime = ExpressionRuntime(renderers=[MockRenderer()])
        
        # Test lifecycle methods exist
        self.assertTrue(hasattr(runtime, 'initialize'))
        self.assertTrue(hasattr(runtime, 'start'))
        self.assertTrue(hasattr(runtime, 'stop'))
        self.assertTrue(hasattr(runtime, 'shutdown'))
        self.assertTrue(hasattr(runtime, 'health'))
        
        # Test health check
        health = runtime.health()
        self.assertEqual(health, HealthState.HEALTHY)


class TestEventBusFunctionality(unittest.TestCase):
    """Test EventBus functionality"""
    
    def test_event_bus_publish_signature(self):
        """Test EventBus.publish exists and can be called"""
        from desktop.app.context import EventBus
        
        bus = EventBus()
        
        # Verify publish method exists
        self.assertTrue(hasattr(bus, 'publish'))
        self.assertTrue(callable(bus.publish))
    
    def test_event_bus_subscribe_exists(self):
        """Test EventBus.subscribe exists"""
        from desktop.app.context import EventBus
        
        bus = EventBus()
        
        # Verify subscribe method exists
        self.assertTrue(hasattr(bus, 'subscribe'))
        self.assertTrue(callable(bus.subscribe))


class TestServiceRegistry(unittest.TestCase):
    """Test ServiceRegistry functionality"""
    
    def test_service_registry_register_resolve(self):
        """Test service registry can register and resolve services"""
        from desktop.app.context import ServiceRegistry
        
        registry = ServiceRegistry()
        
        # Create a simple service
        class TestService:
            def do_something(self):
                return "done"
        
        service = TestService()
        
        # Register
        registry.register(TestService, service)
        
        # Resolve
        resolved = registry.resolve(TestService)
        self.assertIs(resolved, service)
        self.assertEqual(resolved.do_something(), "done")
    
    def test_service_registry_missing_service(self):
        """Test service registry raises error for missing service"""
        from desktop.app.context import ServiceRegistry
        
        registry = ServiceRegistry()
        
        class UnknownService:
            pass
        
        with self.assertRaises(RuntimeError):
            registry.resolve(UnknownService)


class TestAdapters(unittest.TestCase):
    """Test adapter transformations"""
    
    def test_input_adapter_translate(self):
        """Test InputAdapter can translate user requests"""
        from desktop.orchestrator.adapters import InputAdapter
        
        adapter = InputAdapter()
        
        # Translate a user request
        experience = adapter.translate(
            user_request="Open notepad",
            screen_context={"active_window": "browser"},
            vision_context={"objects": []}
        )
        
        # Verify Experience was created
        self.assertIsNotNone(experience)
        self.assertEqual(experience.goal, "Open notepad")
        self.assertIsNotNone(experience.experience_id)
    
    def test_input_adapter_exists(self):
        """Test InputAdapter exists and has translate method"""
        from desktop.orchestrator.adapters import InputAdapter
        
        adapter = InputAdapter()
        self.assertTrue(hasattr(adapter, 'translate'))


class TestCapabilityExecution(unittest.TestCase):
    """Test capability execution"""
    
    def test_execution_step_result_creation(self):
        """Test ExecutionStepResult can be created"""
        from desktop.brain.execution.models import ExecutionStepResult
        
        # Create with defaults
        result1 = ExecutionStepResult()
        self.assertEqual(result1.step_id, "")
        self.assertEqual(result1.status, "")
        
        # Create with values
        result2 = ExecutionStepResult(
            step_id="step_1",
            status="COMPLETED",
            stdout="output",
            stderr="",
            execution_time_ms=100,
            intent="launch_app",
            metadata={"key": "value"}
        )
        self.assertEqual(result2.step_id, "step_1")
        self.assertEqual(result2.status, "COMPLETED")
        self.assertEqual(result2.intent, "launch_app")
    
    def test_capability_results(self):
        """Test capability results"""
        from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus
        
        # Create success result
        success_result = ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            outputs={"result": "value"}
        )
        self.assertEqual(success_result.status, ExecutionStatus.SUCCESS)
        
        # Create failure result
        failure_result = ExecutionResult(
            status=ExecutionStatus.FAILED,
            error_message="Something went wrong"
        )
        self.assertEqual(failure_result.status, ExecutionStatus.FAILED)
        self.assertEqual(failure_result.error_message, "Something went wrong")


class TestPlannerContracts(unittest.TestCase):
    """Test planner contracts and strategies"""
    
    def test_planner_strategy_interface(self):
        """Test planner strategy interface"""
        from desktop.app.planner_contracts import IPlannerStrategy
        
        # Verify interface methods exist
        self.assertTrue(hasattr(IPlannerStrategy, 'parse_intent'))
        self.assertTrue(hasattr(IPlannerStrategy, 'formulate_decision'))
        self.assertTrue(hasattr(IPlannerStrategy, 'create_plan'))
    
    def test_planner_runtime_exists(self):
        """Test PlannerRuntime exists and has correct interface"""
        from desktop.runtimes.planner import PlannerRuntime
        
        self.assertTrue(hasattr(PlannerRuntime, 'process_intent'))
        self.assertTrue(hasattr(PlannerRuntime, 'initialize'))


class TestMemoryService(unittest.TestCase):
    """Test memory service contracts"""
    
    def test_memory_service_interface(self):
        """Test memory service interface"""
        from desktop.app.memory_contracts import IMemoryService
        
        # Verify interface methods exist
        self.assertTrue(hasattr(IMemoryService, 'snapshot'))


class TestCapabilityRegistry(unittest.TestCase):
    """Test capability registry"""
    
    def test_capability_registry_exists(self):
        """Test CapabilityRegistry exists"""
        from desktop.runtimes.capability.registry import CapabilityRegistry
        
        registry = CapabilityRegistry()
        
        # Test registry exists
        self.assertIsNotNone(registry)
        self.assertTrue(hasattr(registry, 'resolve'))


class TestConversationArtifact(unittest.TestCase):
    """Test conversation artifact models"""
    
    def test_interaction_envelope_creation(self):
        """Test InteractionEnvelope can be created with all fields"""
        from desktop.models.interaction import InteractionEnvelope
        
        envelope = InteractionEnvelope(
            id="env_123",
            correlation_id="corr_456",
            timestamp=datetime.now(),
            origin="voice_input",
            transport="local",
            session_id="sess_789",
            user_id="user_001",
            payload="Hello world",
            metadata={"language": "en"}
        )
        
        self.assertEqual(envelope.id, "env_123")
        self.assertEqual(envelope.session_id, "sess_789")
        self.assertEqual(envelope.payload, "Hello world")
        self.assertEqual(envelope.metadata["language"], "en")


class TestCognitiveModels(unittest.TestCase):
    """Test cognitive models"""
    
    def test_cognition_models_exist(self):
        """Test cognition models exist"""
        from desktop.models import cognition
        
        # Verify module exists
        self.assertIsNotNone(cognition)
    
    def test_execution_plan_model_exists(self):
        """Test ExecutionPlan model exists"""
        from desktop.models.cognition import ExecutionPlan
        
        # Just verify the class exists
        self.assertIsNotNone(ExecutionPlan)


if __name__ == '__main__':
    unittest.main(verbosity=2)
