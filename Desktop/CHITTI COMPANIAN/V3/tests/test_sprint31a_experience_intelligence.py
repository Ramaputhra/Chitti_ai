import unittest
import asyncio
from typing import Dict, Any
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.packages.desktop_pack.capabilities.experience_intelligence import (
    ExperienceBuilderCapability,
    ExperienceReflectionCapability,
    ExperienceValidatorCapability
)
from dataclasses import dataclass

def create_tool_invocation(tool_name: str, arguments: Dict[str, Any]) -> ToolInvocation:
    import uuid
    import time
    return ToolInvocation(
        id=f"inv_{uuid.uuid4().hex[:8]}",
        tool_name=tool_name,
        arguments=arguments,
        confidence=1.0,
        source="ExperienceIntelligenceRegressionSuite",
        timestamp=time.time()
    )

class MockExecutionRuntime:
    def __init__(self, registry):
        self.registry = registry
        
    async def execute_plan_async(self, nodes: list):
        print("\n==========================================================")
        print(f"[ExecutionRuntime] Traversing ExecutionPlan for Experience Intelligence Pipeline")
        print("==========================================================")
        results = []
        for node in nodes:
            cap = self.registry.get(node.capability_id)
            inv = create_tool_invocation(node.tool_name, node.arguments)
            out = await cap.execute(inv, None)
            results.append(out)
        return results
    
    def execute_plan(self, nodes: list):
        """Synchronous wrapper for backward compatibility."""
        return asyncio.run(self.execute_plan_async(nodes))

class TestSprint31AExperienceIntelligence(unittest.TestCase):
    def test_experience_intelligence_pipeline(self):
        registry = {
            "ExperienceBuilderCapability": ExperienceBuilderCapability(),
            "ExperienceReflectionCapability": ExperienceReflectionCapability(),
            "ExperienceValidatorCapability": ExperienceValidatorCapability()
        }
        
        executor = MockExecutionRuntime(registry)

        # Define nodes
        nodes = [
            type('Node', (), {'id': 'n1', 'capability_id': 'ExperienceBuilderCapability', 'tool_name': 'experience_build', 'arguments': {}})(),
            type('Node', (), {'id': 'n2', 'capability_id': 'ExperienceReflectionCapability', 'tool_name': 'experience_reflect', 'arguments': {}})(),
            type('Node', (), {'id': 'n3', 'capability_id': 'ExperienceValidatorCapability', 'tool_name': 'experience_validate', 'arguments': {}})(),
        ]
        
        # Execute Pipeline
        results = executor.execute_plan(nodes)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0].data.execution_result.payload["built"])
        self.assertTrue(results[1].data.execution_result.payload["reflected"])
        self.assertTrue(results[2].data.execution_result.payload["validated"])
        
        final_status = results[2].data.execution_result.payload["status"]
        self.assertEqual(final_status, "READY_FOR_MEMORY")
        
        print(f"Experience is VALIDATED.")
        print(f"State = {final_status}.")
        print(f"Pipeline Complete.")

if __name__ == "__main__":
    unittest.main()
