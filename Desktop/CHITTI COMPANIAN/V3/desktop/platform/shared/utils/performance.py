import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from desktop.platform.shared.interfaces.logging import ILoggingService


def measure_time(logger_service: ILoggingService, operation: str) -> Callable[..., Any]:
    """
    A decorator to measure execution time and log it via the LoggingService.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start) * 1000
            logger_service.performance(operation, duration_ms=duration_ms)
            return result

        return wrapper

    return decorator
