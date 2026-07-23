from typing import Dict, Any, List
import uuid

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.execution import ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.knowledge import KnowledgeEdge, FactSource
from desktop.platform.shared.models.memory import Memory, MemoryCategory
from desktop.runtimes.semantic.memory_runtime import MemoryRuntime

class PersistFactCapability(ICapability):
    """
    Capability to explicitly persist a fact into Semantic Memory.
    Adheres to Rule 36 (Writes are explicit via MemoryAPI).
    """
    def __init__(self, memory_runtime: MemoryRuntime):
        self.memory_runtime = memory_runtime

    @property
    def name(self) -> str:
        return "PersistFact"

    @property
    def description(self) -> str:
        return "Persists a new factual relationship (KnowledgeEdge) between two entities in Semantic Memory."

    @property
    def required_permissions(self) -> List[str]:
        return []

    def execute(self, arguments: Dict[str, Any]) -> ExecutionResult:
        source_id = arguments.get("source_id")
        target_id = arguments.get("target_id")
        relationship = arguments.get("relationship")

        if not source_id or not target_id or not relationship:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                output="Missing required arguments: source_id, target_id, or relationship."
            )

        edge = KnowledgeEdge(
            source_id=source_id,
            target_id=target_id,
            relationship=relationship,
            source=FactSource.PLANNER
        )

        validation = self.memory_runtime.store_fact(edge)

        if validation.is_conflict:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                output=f"Fact conflict: {validation.conflict_reason}"
            )

        if validation.is_duplicate:
            return ExecutionResult(
                status=ExecutionStatus.COMPLETED,
                output="Fact is already known."
            )

        return ExecutionResult(
            status=ExecutionStatus.COMPLETED,
            output="Fact persisted successfully."
        )

class UpdatePreferenceCapability(ICapability):
    """
    Capability to explicitly update a user preference in Semantic Memory.
    """
    def __init__(self, memory_runtime: MemoryRuntime):
        self.memory_runtime = memory_runtime

    @property
    def name(self) -> str:
        return "UpdatePreference"

    @property
    def description(self) -> str:
        return "Stores a subjective user preference into Semantic Memory."

    @property
    def required_permissions(self) -> List[str]:
        return []

    def execute(self, arguments: Dict[str, Any]) -> ExecutionResult:
        content = arguments.get("content")
        if not content:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                output="Missing required argument: content."
            )

        memory = Memory(
            content=content,
            category=MemoryCategory.PREFERENCE,
            source=FactSource.PLANNER
        )

        validation = self.memory_runtime.store_memory(memory)

        if validation.is_duplicate:
            return ExecutionResult(
                status=ExecutionStatus.COMPLETED,
                output="Preference is already known."
            )

        if validation.is_valid:
            return ExecutionResult(
                status=ExecutionStatus.COMPLETED,
                output="Preference updated successfully."
            )

        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            output=f"Failed to update preference: {validation.conflict_reason}"
        )
