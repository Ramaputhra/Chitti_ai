import threading
import uuid
from typing import Any, Dict

from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.jobs import IJobManager, JobDefinition, JobStatus
from desktop.platform.shared.interfaces.logging import ILoggingService


class JobManager(IJobManager):
    def __init__(self, event_bus: IEventBus, logger: ILoggingService) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self._jobs: Dict[str, JobStatus] = {}
        self._lock = threading.RLock()

    def submit(
        self, job: JobDefinition, initial_context: Dict[str, Any] | None = None
    ) -> str:
        job_id = str(uuid.uuid4())
        with self._lock:
            self._jobs[job_id] = JobStatus.PENDING

        context = initial_context or {}

        def _run_job() -> None:
            with self._lock:
                self._jobs[job_id] = JobStatus.RUNNING

            self.logger.info(f"Job started: {job.name} ({job_id})")
            try:
                for step in job.steps:
                    step.execute(context)

                with self._lock:
                    self._jobs[job_id] = JobStatus.COMPLETED
                self.logger.info(f"Job completed: {job.name} ({job_id})")
            except Exception as e:
                with self._lock:
                    self._jobs[job_id] = JobStatus.FAILED
                self.logger.exception(e, module="JobManager", job_id=job_id)

        # In a real app, this should run on a ThreadPoolExecutor
        # but for Phase 00, simple daemon threads fulfill the contract.
        t = threading.Thread(target=_run_job, daemon=True)
        t.start()
        return job_id

    def status(self, job_id: str) -> JobStatus:
        with self._lock:
            return self._jobs.get(job_id, JobStatus.FAILED)
