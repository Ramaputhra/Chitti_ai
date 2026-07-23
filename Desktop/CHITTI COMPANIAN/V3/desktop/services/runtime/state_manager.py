from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.state import IStateManager, SystemState


class StateManager(IStateManager):
    def __init__(self, event_bus: IEventBus, logger: ILoggingService) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self._state = SystemState.BOOTING

    def current_state(self) -> SystemState:
        return self._state

    def set_state(self, state: SystemState) -> None:
        if self._state == state:
            return

        old_state = self._state
        self._state = state
        self.logger.info(f"System State transition: {old_state.name} -> {state.name}")

        self.event_bus.publish(
            Event(
                event_id=SystemEvents.STATE_CHANGED,
                source="StateManager",
                payload={"old_state": old_state.name, "new_state": state.name},
            )
        )
