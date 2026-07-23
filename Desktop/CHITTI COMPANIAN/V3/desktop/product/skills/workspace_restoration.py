import re
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.services.capabilities.workspace_capability import WorkspaceCapability
from desktop.services.ui.notification_queue import NotificationQueue


class WorkspaceRestorationWorkflow:
    """
    Workflow P0-007: Restores a workspace profile based on user intent.
    Example: "Open writing workspace" -> Extracts "writing" -> Restores writing.yaml
    """
    def __init__(
        self,
        logger: ILoggingService,
        queue: NotificationQueue,
        workspace_cap: WorkspaceCapability
    ) -> None:
        self.logger = logger
        self.queue = queue
        self.workspace_cap = workspace_cap

    def execute(self, text: str) -> None:
        self.logger.info(f"Starting Workspace Restoration Workflow for: {text}")

        # Extract profile name using regex (e.g., "open writing workspace" -> "writing")
        match = re.search(r'(open|restore|launch)\s+([a-zA-Z0-9_-]+)\s+(workspace|profile)', text.lower())
        
        if match:
            profile_name = match.group(2)
        else:
            # Fallback if the regex fails
            profile_name = "writing"
            for profile in self.workspace_cap.list_profiles():
                if profile in text.lower():
                    profile_name = profile
                    break
                    
        self.logger.info(f"Identified target profile: {profile_name}")
        
        # Execute restoration
        voice_response = self.workspace_cap.execute("restore_profile", {"profile": profile_name})
        
        # Queue Audio Confirmation
        self.queue.enqueue(voice_response)
