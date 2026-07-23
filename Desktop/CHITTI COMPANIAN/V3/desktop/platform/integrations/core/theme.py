from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.theme import IThemeManager


class ThemeManager(IThemeManager):
    """
    Manages Light/Dark and custom themes for the application.
    """
    def __init__(self, event_bus: IEventBus, logger: ILoggingService) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self._current = "dark"

    def apply_theme(self, theme_name: str) -> None:
        self._current = theme_name
        self.logger.info(f"Theme applied: {theme_name}")
        self.event_bus.publish(
            Event(
                event_id=SystemEvents.THEME_CHANGED,
                source="ThemeManager",
                payload={"theme": theme_name},
            )
        )

    def current_theme(self) -> str:
        return self._current
