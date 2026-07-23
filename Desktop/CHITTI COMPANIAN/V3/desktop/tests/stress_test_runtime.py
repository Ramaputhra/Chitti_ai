import time
import tracemalloc

from desktop.platform.shared.di.container import DIContainer
from desktop.platform.shared.interfaces.configuration import IConfigurationService
from desktop.platform.shared.interfaces.event_bus import IEventBus
from desktop.platform.shared.interfaces.lifecycle import AppState, ILifecycleManager
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.resource import IResourceManager
from desktop.platform.shared.interfaces.scheduler import ISchedulerService
from desktop.platform.shared.interfaces.service import IServiceManager
from desktop.platform.shared.interfaces.settings import ISettingsManager
from desktop.platform.shared.interfaces.state import IStateManager
from desktop.platform.shared.interfaces.storage import IStorageManager
from desktop.services.configuration import ConfigurationService
from desktop.platform.integrations.core.event_bus import EventBus
from desktop.platform.integrations.core.lifecycle import LifecycleManager
from desktop.platform.integrations.core.logging_service import LoggingService
from desktop.services.runtime.resource_manager import ResourceManager
from desktop.services.runtime.scheduler_service import SchedulerService
from desktop.services.runtime.service_manager import ServiceManager
from desktop.services.runtime.settings_manager import SettingsManager
from desktop.services.runtime.state_manager import StateManager
from desktop.services.runtime.storage_manager import StorageManager


def run_stress_test(iterations: int = 1000) -> None:
    tracemalloc.start()
    start_time = time.time()
    
    print(f"Starting Runtime Stress Test ({iterations} iterations)...")

    for i in range(iterations):
        container = DIContainer()

        # 1. Register Runtime Core
        container.register_singleton(ILoggingService, LoggingService)
        container.register_singleton(IConfigurationService, ConfigurationService)
        container.register_singleton(IEventBus, EventBus)
        container.register_singleton(ILifecycleManager, LifecycleManager)
        container.register_singleton(IServiceManager, ServiceManager)
        container.register_singleton(ISettingsManager, SettingsManager)
        container.register_singleton(IStorageManager, StorageManager)
        container.register_singleton(IStateManager, StateManager)
        container.register_singleton(ISchedulerService, SchedulerService)
        container.register_singleton(IResourceManager, ResourceManager)

        # 2. Boot
        logger = container.resolve(ILoggingService)
        logger.initialize()

        event_bus = container.resolve(IEventBus)
        event_bus.initialize()

        service_manager = container.resolve(IServiceManager)
        settings = container.resolve(ISettingsManager)
        settings.initialize()

        storage = container.resolve(IStorageManager)
        storage.initialize()

        state = container.resolve(IStateManager)
        
        resource = container.resolve(IResourceManager)
        resource.initialize()

        # 3. Simulate Load
        settings.set("stress_test_var", i)
        storage.backend("keyvalue").set("stress_test_val", i)

        # 4. Graceful Teardown
        event_bus.shutdown()
        logger.shutdown()

        if i % 100 == 0 and i > 0:
            current, peak = tracemalloc.get_traced_memory()
            print(f"Iteration {i}: Memory Current={current/1024:.2f}KB Peak={peak/1024:.2f}KB")

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    print(f"\nStress Test Complete: {iterations} iterations in {end_time - start_time:.2f}s")
    print(f"Final Memory footprint: Current={current/1024:.2f}KB, Peak={peak/1024:.2f}KB")
    tracemalloc.stop()

if __name__ == "__main__":
    run_stress_test(1000)
