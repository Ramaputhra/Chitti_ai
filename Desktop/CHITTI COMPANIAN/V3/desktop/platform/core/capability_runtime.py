import logging
import time
from typing import Any

from desktop.models.execution_models import (
    ExecutionContext, ExecutionStatus, 
    CapabilityStartedEvent, CapabilityCompletedEvent
)
from desktop.platform.components.capabilities.open_folder_adapter import OpenFolderAdapter

logger = logging.getLogger(__name__)

class CapabilityRuntime:
    """
    Rule 38: Executes exactly one ExecutionStep. Unaware of workflows.
    """
    def __init__(self, event_bus: Any):
        self.event_bus = event_bus
        self.adapters = {
            "sys.folder.open": OpenFolderAdapter()
        }

    def execute_step(self, context: ExecutionContext) -> None:
        logger.info(f"CapabilityRuntime: Starting step {context.step_id} ({context.capability_id})")
        
        # 1. Publish STARTED event
        start_event = CapabilityStartedEvent(context=context, timestamp=time.time())
        self.event_bus.publish("CAPABILITY_STARTED", source="CapabilityRuntime", payload={"event": start_event})
        
        # 2. Lookup physical adapter
        adapter = self.adapters.get(context.capability_id)
        if not adapter:
            logger.error(f"No adapter found for {context.capability_id}")
            self._publish_completed(context, ExecutionStatus.FAILED, "Adapter not found")
            return
            
        # 3. Execute
        try:
            if context.capability_id == "sys.folder.open":
                folder_path = context.parameters.get("folder_path")
                success = adapter.execute(folder_path)
                status = ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED
                error_msg = "" if success else "OS launch failed"
                self._publish_completed(context, status, error_msg)
            else:
                self._publish_completed(context, ExecutionStatus.FAILED, "Unsupported capability")
                
        except Exception as e:
            logger.exception(f"CapabilityRuntime failed to execute {context.capability_id}")
            self._publish_completed(context, ExecutionStatus.FAILED, str(e))

    def _publish_completed(self, context: ExecutionContext, status: ExecutionStatus, error_msg: str) -> None:
        comp_event = CapabilityCompletedEvent(
            context=context,
            status=status,
            error_message=error_msg,
            timestamp=time.time()
        )
        self.event_bus.publish("CAPABILITY_COMPLETED", source="CapabilityRuntime", payload={"event": comp_event})
