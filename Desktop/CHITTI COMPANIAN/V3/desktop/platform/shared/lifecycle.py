import time
import sys
from PySide6.QtWidgets import QApplication
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.event_bus import IEventBus, Event
from desktop.platform.shared.models.lifecycle import ShutdownRequest

class LifecycleManager:
    """
    Orchestrates deterministic graceful shutdown pipelines and system tray states.
    """
    def __init__(self, logger: ILoggingService, event_bus: IEventBus):
        self.logger = logger
        self.event_bus = event_bus
        self.is_shutting_down = False
        
        # Subscribe to shutdown request event
        self.event_bus.subscribe("System.ShutdownRequest", self._on_shutdown_request)

    def _on_shutdown_request(self, event: Event):
        if not isinstance(event.data, ShutdownRequest):
            self.logger.warning("Invalid shutdown request received.")
            return
            
        request: ShutdownRequest = event.data
        self.logger.info(f"Shutdown requested. Reason: {request.reason.value}. Message: {request.message}")
        self.execute_shutdown_pipeline()

    def execute_shutdown_pipeline(self):
        if self.is_shutting_down:
            return
            
        self.is_shutting_down = True
        self.logger.info("Executing graceful shutdown pipeline...")
        
        # 1. Stop New Tasks
        self.logger.info("Step 1: Stopping new tasks...")
        self.event_bus.publish(Event("Lifecycle.StopNewTasks", None))
        
        # 2. Wait for Current Atomic Step
        self.logger.info("Step 2: Waiting for current atomic step to complete...")
        self.event_bus.publish(Event("Lifecycle.WaitAtomicStep", None))
        time.sleep(0.5) # Simulated wait; in real implementation, await signals from TaskRuntime
        
        # 3. Cancel Background Work
        self.logger.info("Step 3: Canceling background work...")
        self.event_bus.publish(Event("Lifecycle.CancelBackground", None))
        
        # 4. Flush Logs
        self.logger.info("Step 4: Flushing logs...")
        self.event_bus.publish(Event("Lifecycle.FlushLogs", None))
        
        # 5. Save Checkpoints
        self.logger.info("Step 5: Saving checkpoints...")
        self.event_bus.publish(Event("Lifecycle.SaveCheckpoints", None))
        
        # 6. Shutdown Capabilities
        self.logger.info("Step 6: Shutting down capabilities...")
        self.event_bus.publish(Event("Lifecycle.ShutdownCapabilities", None))
        
        # 7. Shutdown Runtimes
        self.logger.info("Step 7: Shutting down runtimes...")
        self.event_bus.publish(Event("Lifecycle.ShutdownRuntimes", None))
        
        # 8. Remove Tray
        self.logger.info("Step 8: Removing system tray...")
        self.event_bus.publish(Event("Lifecycle.RemoveTray", None))
        
        # 9. Quit Qt
        self.logger.info("Step 9: Quitting application...")
        app = QApplication.instance()
        if app:
            app.quit()
        else:
            self._publish_exit_code()
            sys.exit(0)

    def _publish_exit_code(self):
        # 10. Exit Code Published
        self.logger.info("Step 10: Exit Code Published.")
        self.event_bus.publish(Event("Lifecycle.ExitCode", {"code": 0}))
