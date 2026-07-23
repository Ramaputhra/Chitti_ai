import asyncio
from typing import Callable, Awaitable
from desktop.ui.presence.presence_state import PresenceState

class IdleManager:
    """
    Handles automatic state transitions for Idle behavior.
    READY -> 2 min -> EXERCISING -> 5 min -> GOODBYE -> SLEEPING
    """
    def __init__(self, push_state: Callable[[PresenceState], Awaitable[None]]):
        self._push_state = push_state
        self._timer_task = None
        
        # Reduced for MVP demonstration. 
        # In production: 120s and 300s.
        self._exercising_timeout_sec = 120
        self._sleeping_timeout_sec = 300

    def on_state_changed(self, new_state: PresenceState):
        # Cancel any existing timer
        if self._timer_task:
            self._timer_task.cancel()
            self._timer_task = None

        if new_state in (PresenceState.READY, PresenceState.IDLE):
            self._timer_task = asyncio.create_task(self._start_exercising_timer())
        elif new_state == PresenceState.EXERCISING:
            self._timer_task = asyncio.create_task(self._start_sleeping_timer())

    async def _start_exercising_timer(self):
        try:
            await asyncio.sleep(self._exercising_timeout_sec)
            await self._push_state(PresenceState.EXERCISING)
        except asyncio.CancelledError:
            pass

    async def _start_sleeping_timer(self):
        try:
            await asyncio.sleep(self._sleeping_timeout_sec)
            await self._push_state(PresenceState.GOODBYE)
            await asyncio.sleep(1.5) # Wait for goodbye animation
            await self._push_state(PresenceState.SLEEPING)
        except asyncio.CancelledError:
            pass
