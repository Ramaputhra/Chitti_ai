import os
import sys
from typing import Any

from loguru import logger

from desktop.platform.shared.interfaces.logging import ILoggingService


class LoggingService(ILoggingService):
    def __init__(self, log_dir: str = "logs") -> None:
        self.log_dir = log_dir

    def initialize(self) -> None:
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Remove default handler
        logger.remove()

        # Stdout for startup
        logger.add(sys.stdout, level="DEBUG", format="{time} | {level} | {message} | {extra}")

        # Core log files
        base_format = "{time} | {level} | {message} | {extra}"

        # 1. Debug log (Everything)
        logger.add(
            os.path.join(self.log_dir, "debug.log"),
            level="DEBUG",
            rotation="10 MB",
            compression="zip",
            format=base_format,
        )

        # 2. Application log (Info and above)
        logger.add(
            os.path.join(self.log_dir, "application.log"),
            level="INFO",
            rotation="10 MB",
            compression="zip",
            format=base_format,
        )

        # 3. Errors log (Errors and criticals)
        logger.add(
            os.path.join(self.log_dir, "errors.log"),
            level="ERROR",
            rotation="10 MB",
            compression="zip",
            format=base_format,
        )

        # 4. Performance log (Filter by performance flag)
        logger.add(
            os.path.join(self.log_dir, "performance.log"),
            filter=lambda record: record["extra"].get("is_performance", False),
            rotation="10 MB",
            compression="zip",
            format=base_format,
        )

        # 5. Events log (Filter by event flag)
        logger.add(
            os.path.join(self.log_dir, "events.log"),
            filter=lambda record: record["extra"].get("is_event", False),
            rotation="10 MB",
            compression="zip",
            format=base_format,
        )

    def shutdown(self) -> None:
        logger.remove()

    def debug(self, msg: str, **kwargs: Any) -> None:
        logger.bind(**kwargs).debug(msg)

    def info(self, msg: str, **kwargs: Any) -> None:
        logger.bind(**kwargs).info(msg)

    def warning(self, msg: str, **kwargs: Any) -> None:
        logger.bind(**kwargs).warning(msg)

    def error(self, msg: str, **kwargs: Any) -> None:
        logger.bind(**kwargs).error(msg)

    def critical(self, msg: str, **kwargs: Any) -> None:
        logger.bind(**kwargs).critical(msg)

    def event(self, event_id: str, module: str, **kwargs: Any) -> None:
        logger.bind(is_event=True, event_id=event_id, module=module, **kwargs).info(
            f"Event: {event_id}"
        )

    def performance(self, operation: str, duration_ms: float, **kwargs: Any) -> None:
        logger.bind(is_performance=True, operation=operation, duration_ms=duration_ms, **kwargs).info(
            f"Performance: {operation} took {duration_ms:.2f}ms"
        )

    def exception(self, exc: BaseException, **kwargs: Any) -> None:
        logger.bind(**kwargs).exception(exc)
