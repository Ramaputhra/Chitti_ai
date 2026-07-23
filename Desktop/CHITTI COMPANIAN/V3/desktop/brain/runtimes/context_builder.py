from dataclasses import dataclass
from typing import List

# Type stubs for things we don't import here directly to keep this file simple
class Goal: pass
class GoalContext: pass
class MemoryAPI: pass
class GoalGraphAPI: pass
class TaskAPI: pass
class SystemStateAPI: pass

@dataclass(frozen=True)
class KnowledgeRetrievalPolicy:
    """Rules for selecting knowledge based on Evidence Evaluation."""
    minimum_trust_score: float
    require_consensus: bool
    max_records: int
    prioritize_recency: bool

@dataclass(frozen=True)
class ConstraintAssemblyPolicy:
    """Rules for resolving environmental and system constraints."""
    include_system_constraints: bool
    include_user_preferences: bool

@dataclass(frozen=True)
class RelatedGoalPolicy:
    """Rules for discovering related goals in the graph."""
    max_depth: int
    relationship_types: List[str]
    include_completed: bool

@dataclass(frozen=True)
class PendingWorkPolicy:
    """Rules for collecting active workflows and tasks."""
    include_suspended: bool
    include_active_workflows: bool

@dataclass(frozen=True)
class ContextAssemblyPipeline:
    """The formal configuration for building a specific GoalContext."""
    knowledge_policy: KnowledgeRetrievalPolicy
    constraint_policy: ConstraintAssemblyPolicy
    related_goal_policy: RelatedGoalPolicy
    pending_work_policy: PendingWorkPolicy

class GoalContextBuilder:
    """
    Transforms a Goal into a GoalContext using deterministic policies.
    """
    def __init__(
        self,
        memory_api: MemoryAPI,
        goal_graph_api: GoalGraphAPI,
        task_api: TaskAPI,
        system_state_api: SystemStateAPI
    ):
        self.memory = memory_api
        self.goals = goal_graph_api
        self.tasks = task_api
        self.system_state = system_state_api
        
    def assemble_context(self, goal: Goal, pipeline: ContextAssemblyPipeline) -> GoalContext:
        """
        Executes:
        1. Knowledge Retrieval
        2. Constraint Resolution (including dynamic constraints via System State API)
        3. Related Goal Discovery
        4. Pending Work Collection
        Returns an immutable GoalContext snapshot (with ContextMetadata).
        """
        pass
