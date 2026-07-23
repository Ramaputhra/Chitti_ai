from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.lifecycle import AppState, ILifecycleManager
from desktop.platform.shared.interfaces.logging import ILoggingService


class LifecycleManager(ILifecycleManager):
    """
    Controls the strict state transitions of the CHITTI application.
    """
    def __init__(self, event_bus: IEventBus, logger: ILoggingService) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self._state = AppState.BOOTING

    @property
    def current_state(self) -> AppState:
        return self._state

    def transition_to(self, new_state: AppState) -> None:
        old_state = self._state
        self._state = new_state
        self.logger.info(f"Lifecycle transition: {old_state.name} -> {new_state.name}")

        event_map = {
            AppState.BOOTING: SystemEvents.APP_STARTING,
            AppState.READY: SystemEvents.APP_STARTED,
            AppState.SHUTTING_DOWN: SystemEvents.APP_STOPPING,
        }

        if new_state in event_map:
            self.event_bus.publish(
                Event(
                    event_id=event_map[new_state],
                    source="LifecycleManager",
                    payload={"old_state": old_state.name, "new_state": new_state.name},
                )
            )
