import unittest
from typing import Dict, Any
from desktop.platform.shared.models.workflow import Workflow, WorkflowStep
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.packages.desktop_pack.capabilities.experience_intelligence import (
    ExperienceBuilderCapability,
    ExperienceReflectionCapability,
    ExperienceValidatorCapability
)
from dataclasses import dataclass

@dataclass
class ExecutionPlanNode:
    id: str
    capability_id: str
    tool_name: str
    arguments: Dict[str, Any]
    dependencies: list = None

def create_tool_invocation(tool_name: str, arguments: Dict[str, Any]) -> ToolInvocation:
    import uuid
    return ToolInvocation(
        id=f"inv_{uuid.uuid4().hex[:8]}",
        tool_name=tool_name,
        arguments=arguments,
        confidence=1.0,
        source="ExperienceIntelligenceRegressionSuite"
    )

class MockExecutionRuntime:
    def __init__(self, registry):
        self.registry = registry
        
    def execute_plan(self, nodes: list):
        print("\n==========================================================")
        print(f"[ExecutionRuntime] Traversing ExecutionPlan for Experience Intelligence Pipeline")
        print("==========================================================")
        results = []
        for node in nodes:
            cap = self.registry.get(node.capability_id)
            out = cap.execute(create_tool_invocation(node.tool_name, node.arguments))
            results.append(out)
        return results

class TestSprint31AExperienceIntelligence(unittest.TestCase):
    def test_experience_intelligence_pipeline(self):
        registry = {
            "ExperienceBuilderCapability": ExperienceBuilderCapability(),
            "ExperienceReflectionCapability": ExperienceReflectionCapability(),
            "ExperienceValidatorCapability": ExperienceValidatorCapability()
        }
        
        executor = MockExecutionRuntime(registry)

        # Define Pipeline DAG
        n1 = ExecutionPlanNode("n1", "ExperienceBuilderCapability", "experience_build", {})
        n2 = ExecutionPlanNode("n2", "ExperienceReflectionCapability", "experience_reflect", {}, dependencies=["n1"])
        n3 = ExecutionPlanNode("n3", "ExperienceValidatorCapability", "experience_validate", {}, dependencies=["n2"])
        
        # Execute Pipeline
        results = executor.execute_plan([n1, n2, n3])
        
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0].execution_result.payload["built"])
        self.assertTrue(results[1].execution_result.payload["reflected"])
        self.assertTrue(results[2].execution_result.payload["validated"])
        
        final_status = results[2].execution_result.payload["status"]
        self.assertEqual(final_status, "READY_FOR_MEMORY")
        
        print(f"Experience is VALIDATED.")
        print(f"State = {final_status}.")
        print(f"Pipeline Complete.")

if __name__ == "__main__":
    unittest.main()
