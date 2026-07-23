from pathlib import Path
from typing import Callable
from datetime import datetime, timezone
from desktop.core.runtime import (
    IRuntime, RuntimeMetadata, RuntimePriority, RuntimeTraits,
    HealthPolicy, RestartPolicy, RuntimeState, HealthPayload
)
from desktop.models.events import SystemEvent
from desktop.workflow.models import WorkflowState, WorkflowFailed
from desktop.planner.models import WorkflowPlanningCompleted
from desktop.execution_graph.models import (
    ExecutionNode, ExecutionGraph, ExecutionGraphBuildingStarted,
    ExecutionGraphReady, GraphValidationFailed, WorkflowReadyForScheduling
)

class ExecutionGraphRuntime(IRuntime):
    def __init__(self, publish_event: Callable[[SystemEvent], None]):
        self._publish = publish_event
        self._state = RuntimeState.CREATED
        self._health = HealthPayload(True, self._state, datetime.now(timezone.utc), 0.0)
        self._metadata = RuntimeMetadata(
            runtime_id="ExecutionGraphRuntime",
            api_version="1.0",
            priority=RuntimePriority.HIGH,
            dependencies=["PlannerRuntime"],
            traits=RuntimeTraits(background=True),
            health_policy=HealthPolicy(interval_seconds=2.0),
            restart_policy=RestartPolicy.ALWAYS
        )

    def get_metadata(self) -> RuntimeMetadata:
        return self._metadata
        
    def get_state(self) -> RuntimeState:
        return self._state
        
    async def initialize(self) -> None:
        self._state = RuntimeState.INITIALIZING
        self._state = RuntimeState.READY
        
    async def start(self) -> None:
        self._state = RuntimeState.RUNNING
        
    async def stop(self) -> None:
        self._state = RuntimeState.STOPPED
        
    async def health_check(self) -> HealthPayload:
        self._health.state = self._state
        self._health.last_heartbeat = datetime.now(timezone.utc)
        return self._health

    def _validate_graph(self, graph: ExecutionGraph) -> bool:
        if not graph.nodes:
            return False
        seen = set()
        for node in graph.nodes:
            if node.node_id in seen:
                return False
            seen.add(node.node_id)
        return True

    async def handle_workflow_planning_completed(self, event: WorkflowPlanningCompleted) -> None:
        if self._state != RuntimeState.RUNNING:
            return
            
        instance = event.instance
        planned_workflow = event.planned_workflow
        
        instance.state = WorkflowState.GRAPH_BUILDING
        self._publish(ExecutionGraphBuildingStarted(instance=instance))
        
        graph = ExecutionGraph()
        
        previous_node_id = None
        for step in planned_workflow.steps:
            node = ExecutionNode(
                node_id=step.id,
                capability=step.capability,
                inputs=step.params,
                timeout=step.params.get("timeout", 30),
                retry=step.params.get("retry", 0)
            )
            graph.nodes.append(node)
            
            if previous_node_id:
                graph.edges.append({"from": previous_node_id, "to": step.id})
                
            previous_node_id = step.id
            
        if not self._validate_graph(graph):
            self._publish(GraphValidationFailed(instance=instance, reason="Cycle detected or invalid nodes"))
            instance.state = WorkflowState.FAILED
            self._publish(WorkflowFailed(instance=instance, reason="Graph validation failed"))
            return
            
        instance.state = WorkflowState.GRAPH_READY
        self._publish(ExecutionGraphReady(instance=instance, graph=graph))
        
        instance.state = WorkflowState.SCHEDULING
        self._publish(WorkflowReadyForScheduling(instance=instance))
