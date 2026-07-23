import asyncio
import time
from collections import deque
from typing import Optional, Callable, Awaitable, Any
from desktop.ui.presence.presence_state import PresenceState, PresencePriority

class AnimationQueue:
    """
    Manages state transitions.
    Ensures non-interruptible states complete their minimum duration before the next state is applied.
    """
    def __init__(self, on_state_change: Callable[[PresenceState, Optional[Any]], Awaitable[None]]):
        self._queue = deque() # tuples of (state, context)
        self._current_state: Optional[PresenceState] = None
        self._current_context: Optional[Any] = None
        self._state_start_time: float = 0.0
        self._on_state_change = on_state_change
        self._task: Optional[asyncio.Task] = None
        self._running = False
        
    def start(self):
        self._running = True
        self._task = asyncio.create_task(self._process_queue())

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

    async def push(self, state: PresenceState, context: Optional[Any] = None):
        # Always queue the incoming state to not lose it
        self._queue.append((state, context))
        
        # If we have no state, or current state is interruptible, or new state is CRITICAL
        if self._current_state is None:
            self._force_next()
        elif state.metadata.priority == PresencePriority.CRITICAL:
            # Critical errors interrupt everything
            self._force_next()
        elif self._current_state.metadata.interruptible:
            # If current state is interruptible, check if it met its minimum duration.
            elapsed = (time.time() - self._state_start_time) * 1000
            if elapsed >= self._current_state.metadata.min_duration_ms:
                self._force_next()

    def _force_next(self):
        """Immediately bypasses queue wait times and applies the most recent state that makes sense."""
        if not self._queue:
            return
            
        # Find highest priority in queue
        highest_prio_item = max(self._queue, key=lambda item: item[0].metadata.priority.value)
        
        # Clear queue and apply it
        self._queue.clear()
        self._apply_state(highest_prio_item[0], highest_prio_item[1])

    def _apply_state(self, state: PresenceState, context: Optional[Any] = None):
        self._current_state = state
        self._current_context = context
        self._state_start_time = time.time()
        
        asyncio.create_task(self._on_state_change(state, context))

    async def _process_queue(self):
        """Background loop to naturally drain the queue when minimum durations are met."""
        while self._running:
            await asyncio.sleep(0.05) # 50ms tick
            
            if not self._current_state or not self._queue:
                continue
                
            elapsed = (time.time() - self._state_start_time) * 1000
            
            # If current state is finished its minimum duration
            if elapsed >= self._current_state.metadata.min_duration_ms:
                # If current state is NOT interruptible, it blocks until duration is met, then we switch
                # If it IS interruptible, it might have been blocked by min_duration, now we switch
                self._force_next()
