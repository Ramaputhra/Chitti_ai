import unittest
import asyncio
from pathlib import Path
from desktop.intent.models import IntentRecognized
from desktop.workflow.models import (
    WorkflowCreated, WorkflowValidated, WorkflowReady, WorkflowState
)
from desktop.workflow.runtime import WorkflowRuntime
from desktop.planner.models import WorkflowPlanningStarted, WorkflowPlanningCompleted
from desktop.planner.runtime import PlannerRuntime
from desktop.execution_graph.models import (
    ExecutionGraphBuildingStarted, ExecutionGraphReady, WorkflowReadyForScheduling
)
from desktop.execution_graph.runtime import ExecutionGraphRuntime

class TestWorkflowOrchestration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.config_dir = Path(r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\desktop\config")
        self.events = []
        
        def publish(event):
            self.events.append(event)
            
        self.wf_runtime = WorkflowRuntime(publish, self.config_dir)
        self.pl_runtime = PlannerRuntime(publish, self.config_dir)
        self.eg_runtime = ExecutionGraphRuntime(publish)
        
        await self.wf_runtime.initialize()
        await self.pl_runtime.initialize()
        await self.eg_runtime.initialize()
        
        await self.wf_runtime.start()
        await self.pl_runtime.start()
        await self.eg_runtime.start()

    async def asyncTearDown(self):
        await self.wf_runtime.stop()
        await self.pl_runtime.stop()
        await self.eg_runtime.stop()

    async def test_workflow_orchestration_pipeline(self):
        intent_event = IntentRecognized(
            intent_id="OPEN_APPLICATION",
            entities={"app_name": "chrome.exe"},
            language="en"
        )
        
        await self.wf_runtime.handle_intent_recognized(intent_event)
        
        wf_created_events = [e for e in self.events if isinstance(e, WorkflowCreated)]
        self.assertEqual(len(wf_created_events), 1)
        instance = wf_created_events[0].instance
        self.assertTrue(instance.instance_id.startswith("WF-"))
        
        # Pass to Planner
        await self.pl_runtime.handle_workflow_created(wf_created_events[0])
        
        pl_started = [e for e in self.events if isinstance(e, WorkflowPlanningStarted)]
        self.assertEqual(len(pl_started), 1)
        
        pl_completed = [e for e in self.events if isinstance(e, WorkflowPlanningCompleted)]
        self.assertEqual(len(pl_completed), 1)
        planned_wf = pl_completed[0].planned_workflow
        self.assertEqual(len(planned_wf.steps), 3) 
        self.assertEqual(planned_wf.steps[0].capability, "ResolveEntity")
        
        # Pass to Execution Graph
        await self.eg_runtime.handle_workflow_planning_completed(pl_completed[0])
        
        eg_started = [e for e in self.events if isinstance(e, ExecutionGraphBuildingStarted)]
        self.assertEqual(len(eg_started), 1)
        
        eg_ready = [e for e in self.events if isinstance(e, ExecutionGraphReady)]
        self.assertEqual(len(eg_ready), 1)
        
        wf_scheduled = [e for e in self.events if isinstance(e, WorkflowReadyForScheduling)]
        self.assertEqual(len(wf_scheduled), 1)
        
        graph = eg_ready[0].graph
        self.assertEqual(len(graph.nodes), 3)
        self.assertEqual(len(graph.edges), 2)
        
        self.assertEqual(graph.nodes[0].node_id, "resolve_app")
        self.assertEqual(graph.nodes[1].node_id, "launch_app")
        self.assertEqual(graph.edges[0]["from"], "resolve_app")
        self.assertEqual(graph.edges[0]["to"], "launch_app")

if __name__ == '__main__':
    unittest.main()
