import time
from typing import Dict, Optional

from desktop.platform.shared.kernel.models import CancellationToken

class CancellationManager:
    """
    Manages CancellationToken lifecycle for running workflows and steps.
    """
    def __init__(self) -> None:
        # Map of workflow_id -> CancellationToken
        self._tokens: Dict[str, CancellationToken] = {}

    def create_token(self, workflow_id: str) -> CancellationToken:
        """Create a new token for a workflow."""
        token = CancellationToken()
        self._tokens[workflow_id] = token
        return token

    def get_token(self, workflow_id: str) -> Optional[CancellationToken]:
        """Retrieve an existing token."""
        return self._tokens.get(workflow_id)

    def request_cancellation(self, workflow_id: str, reason: str, requested_by: str) -> None:
        """
        Flag a workflow's token as cancelled.
        The executor checks this token periodically or at step boundaries.
        """
        token = self._tokens.get(workflow_id)
        if token:
            token.cancel(reason=reason, requested_by=requested_by)

    def cleanup_token(self, workflow_id: str) -> None:
        """Remove a token from tracking once the workflow completes."""
        self._tokens.pop(workflow_id, None)
