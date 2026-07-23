from typing import Any, Callable, Protocol


class ISchedulerService(Protocol):
    """
    Manages delayed and periodic background tasks via timers.
    Used for 'Run Later' logic, independent of heavy workflows.
    """
    def run_later(self, delay_seconds: float, callback: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
        """Schedules a function to run after a delay. Returns a task ID."""
        ...

    def run_every(self, interval_seconds: float, callback: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
        """Schedules a function to run periodically. Returns a task ID."""
        ...

    def cancel(self, task_id: str) -> None:
        """Cancels a scheduled task if it hasn't executed yet."""
        ...
