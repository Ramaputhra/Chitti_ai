from typing import Any, Protocol

class ILoggingService(Protocol):
    """
    Interface for the CHITTI Logging Service.
    All modules must depend on this interface, never directly on Loguru.
    """

    def initialize(self) -> None:
        """Initializes the logging system, setting up handlers and rotators."""
        ...

    def shutdown(self) -> None:
        """Safely shuts down the logging system."""
        ...

    def debug(self, msg: str, **kwargs: Any) -> None:
        """Log a debug message."""
        ...

    def info(self, msg: str, **kwargs: Any) -> None:
        """Log an info message."""
        ...

    def warning(self, msg: str, **kwargs: Any) -> None:
        """Log a warning message."""
        ...

    def error(self, msg: str, **kwargs: Any) -> None:
        """Log an error message."""
        ...

    def critical(self, msg: str, **kwargs: Any) -> None:
        """Log a critical message."""
        ...

    def event(self, event_id: str, module: str, **kwargs: Any) -> None:
        """Log a structured system event (e.g., THEME_CHANGED)."""
        ...

    def performance(self, operation: str, duration_ms: float, **kwargs: Any) -> None:
        """Log performance metrics."""
        ...

    def exception(self, exc: BaseException, **kwargs: Any) -> None:
        """Log an exception with a full stack trace."""
        ...
