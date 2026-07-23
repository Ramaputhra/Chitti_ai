from typing import Dict, List, Optional
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.logger import ILoggingService
from desktop.platform.shared.interfaces.event_bus import IEventBus, Event
from desktop.platform.shared.models.task import TaskContext, TaskState
from desktop.services.tasks.policies import TaskPolicy

class TaskScheduler:
    """
    Manages queued tasks, priorities, pausing, resuming, and cancellation.
    Sits in front of the TaskRuntime.
    """
    def __init__(self, logger: ILoggingService, event_bus: IEventBus):
        self.logger = logger
        self.event_bus = event_bus
        self._state = ServiceState.STOPPED
        
        # In-memory queue
        self.queued_tasks: List[TaskContext] = []
        self.active_tasks: Dict[str, TaskContext] = {}
        
        # Concurrency limit (could be configured per policy, but for now system-wide max)
        self.max_concurrent_tasks = 2

    @property
    def name(self) -> str:
        return "TaskScheduler"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.event_bus.subscribe(SystemEvents.TASK_CREATED, self._on_task_created)
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def _on_task_created(self, event: Event) -> None:
        goal = event.payload.get("goal", "")
        source_intent = event.payload.get("source_intent", "Unknown")
        correlation_id = event.payload.get("correlation_id", "")
        context = TaskContext(
            goal=goal,
            source_intent=source_intent,
            correlation_id=correlation_id,
            state=TaskState.CREATED
        )
        self.schedule(context)

    def schedule(self, context: TaskContext, policy: Optional[TaskPolicy] = None) -> None:
        """Schedules a new task for execution."""
        self.logger.info(f"Scheduling task {context.task_id} (Goal: {context.goal})")
        context.state = TaskState.CREATED
        self.queued_tasks.append(context)
        self._pump()

    def cancel(self, task_id: str) -> None:
        """Cancels a queued or running task."""
        # Check queue
        for t in self.queued_tasks:
            if t.task_id == task_id:
                t.state = TaskState.CANCELLED
                self.queued_tasks.remove(t)
                self.logger.info(f"Cancelled queued task {task_id}")
                return
                
        # Check active
        if task_id in self.active_tasks:
            t = self.active_tasks[task_id]
            t.state = TaskState.CANCELLED
            self.logger.info(f"Cancelled active task {task_id}")
            del self.active_tasks[task_id]
            self._pump()

    def complete_task(self, task_id: str) -> None:
        """Called by TaskRuntime when a task finishes (success or fail)."""
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
            self._pump()

    def _pump(self) -> None:
        """Pumps tasks from the queue to the active pool based on concurrency limits."""
        while len(self.active_tasks) < self.max_concurrent_tasks and self.queued_tasks:
            task = self.queued_tasks.pop(0)
            self.active_tasks[task.task_id] = task
            self.logger.info(f"Starting scheduled task {task.task_id}")
            self.event_bus.publish(Event(
                "Task.Started",
                self.name,
                {"task_context": task}
            ))
