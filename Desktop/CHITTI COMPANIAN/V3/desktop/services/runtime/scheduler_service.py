import threading
import uuid
from typing import Any, Callable, Dict

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.scheduler import ISchedulerService


class SchedulerService(ISchedulerService):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._timers: Dict[str, threading.Timer] = {}
        self._lock = threading.RLock()

    def _execute(
        self, task_id: str, callback: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        with self._lock:
            if task_id in self._timers:
                del self._timers[task_id]
        try:
            callback(*args, **kwargs)
        except Exception as e:
            self.logger.exception(e, module="Scheduler", task_id=task_id)

    def _execute_periodic(
        self,
        task_id: str,
        interval: float,
        callback: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        try:
            callback(*args, **kwargs)
        except Exception as e:
            self.logger.exception(e, module="Scheduler", task_id=task_id)

        with self._lock:
            # Re-schedule only if it wasn't cancelled during execution
            if task_id in self._timers:
                timer = threading.Timer(
                    interval,
                    self._execute_periodic,
                    args=(task_id, interval, callback) + args,
                    kwargs=kwargs,
                )
                timer.daemon = True
                self._timers[task_id] = timer
                timer.start()

    def run_later(
        self, delay_seconds: float, callback: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> str:
        task_id = str(uuid.uuid4())
        timer = threading.Timer(
            delay_seconds, self._execute, args=(task_id, callback) + args, kwargs=kwargs
        )
        timer.daemon = True
        with self._lock:
            self._timers[task_id] = timer
        timer.start()
        return task_id

    def run_every(
        self,
        interval_seconds: float,
        callback: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> str:
        task_id = str(uuid.uuid4())
        timer = threading.Timer(
            interval_seconds,
            self._execute_periodic,
            args=(task_id, interval_seconds, callback) + args,
            kwargs=kwargs,
        )
        timer.daemon = True
        with self._lock:
            self._timers[task_id] = timer
        timer.start()
        return task_id

    def cancel(self, task_id: str) -> None:
        with self._lock:
            if task_id in self._timers:
                self._timers[task_id].cancel()
                del self._timers[task_id]
