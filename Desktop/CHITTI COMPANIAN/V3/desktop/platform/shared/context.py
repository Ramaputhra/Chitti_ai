from dataclasses import dataclass

from desktop.platform.shared.interfaces.configuration import IConfigurationService
from desktop.platform.shared.interfaces.event_bus import IEventBus
from desktop.platform.shared.interfaces.lifecycle import ILifecycleManager
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.theme import IThemeManager
from desktop.platform.shared.interfaces.version import IVersionManager


@dataclass(frozen=True)
class ApplicationContext:
    """
    Immutable snapshot of the core foundation services.
    This is NOT a Service Locator. Do not add get(), resolve(), or register() methods here.
    """
    config: IConfigurationService
    logger: ILoggingService
    version: IVersionManager
    event_bus: IEventBus
    lifecycle: ILifecycleManager
    theme: IThemeManager
