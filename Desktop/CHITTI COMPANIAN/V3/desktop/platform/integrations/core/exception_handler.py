import sys
import platform
import traceback
from typing import Any, Type

from desktop.platform.shared.interfaces.logging import ILoggingService


class GlobalExceptionHandler:
    """
    Catches all unhandled exceptions globally and logs them cleanly with OS and context data.
    """
    def __init__(self, logger: ILoggingService, app_version: str = "0.1.0") -> None:
        self.logger = logger
        self.app_version = app_version

    def hook(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_traceback: Any
    ) -> None:
        # Allow normal Ctrl+C behavior
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        stack = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        module = "unknown"
        if exc_traceback and exc_traceback.tb_frame:
            module = exc_traceback.tb_frame.f_globals.get("__name__", "unknown")

        self.logger.critical(
            "Unhandled Exception",
            is_event=True,
            event_id="UNHANDLED_EXCEPTION",
            module=module,
            exception_type=exc_type.__name__,
            error_message=str(exc_value),
            stack_trace=stack,
            app_version=self.app_version,
            os_info=f"{platform.system()} {platform.release()}",
            python_version=platform.python_version()
        )
        
        # Future: Emit event to EventBus to show UI crash dialog before exiting.

    def register(self) -> None:
        """Hooks into the sys module to capture global exceptions."""
        sys.excepthook = self.hook
