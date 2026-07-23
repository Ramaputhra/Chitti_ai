from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.context import UnifiedContext


class IContextEngine(IService):
    """
    Aggregates various signals (State, Task, Conversation, Vision) into a single
    UnifiedContext object that the rest of the Language Runtime can use.
    """
    def get_current_context(self) -> UnifiedContext:
        """Returns a snapshot of the current state of the world."""
        ...

    def update_task(self, task_name: str) -> None:
        """Sets the current active background task."""
        ...
