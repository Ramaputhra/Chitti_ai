import collections
import logging
from typing import List, Optional
from desktop.models.presentation import (
    PresentationCommand, RenderCommand, CloseCommand, PatchCommand, FocusCommand
)

class PresentationCommandQueue:
    """
    Batches, throttles, and coalesces UI commands before transmitting them to the renderer.
    """
    def __init__(self):
        # In a real implementation this would be a PriorityQueue.
        # Stubbing with a deque for architectural scaffolding.
        self.queue: collections.deque[PresentationCommand] = collections.deque()
        
    def enqueue(self, command: PresentationCommand):
        """
        Inserts a command into the queue and applies coalescing rules.
        """
        self._coalesce(command)
        
    def _coalesce(self, new_command: PresentationCommand):
        """
        Applies batching heuristics.
        E.g., if there are multiple FocusCommands for the same session, keep the latest.
        """
        # Stub implementation of coalescing rules.
        if isinstance(new_command, CloseCommand):
            # A close command implies we can drop all pending patches for this session
            self.queue = collections.deque(
                [cmd for cmd in self.queue if cmd.session_id != new_command.session_id]
            )
            self.queue.append(new_command)
            logging.debug(f"Queue: Dropped pending commands for closing session {new_command.session_id}")
            
        elif isinstance(new_command, FocusCommand):
            # Drop older focus commands for this session
            self.queue = collections.deque(
                [cmd for cmd in self.queue if not (isinstance(cmd, FocusCommand) and cmd.session_id == new_command.session_id)]
            )
            self.queue.append(new_command)
            
        else:
            # Default behavior: append to end
            # In the future, this is where rapid sequential PatchCommands would be deeply merged.
            self.queue.append(new_command)

    def dequeue_batch(self, max_items: int = 10) -> List[PresentationCommand]:
        """
        Pulls a batch of processed commands ready for transport.
        """
        batch = []
        while self.queue and len(batch) < max_items:
            batch.append(self.queue.popleft())
        return batch
