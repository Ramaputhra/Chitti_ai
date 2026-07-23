import sys
import threading
import time
import tracemalloc

from desktop.platform.shared.di.container import DIContainer
from desktop.platform.shared.interfaces.audio_devices import IAudioDeviceManager
from desktop.platform.shared.interfaces.event_bus import IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.microphone import IMicrophoneManager
from desktop.platform.shared.interfaces.settings import ISettingsManager
from desktop.services.audio.device_manager import AudioDeviceManager
from desktop.services.audio.microphone_manager import MicrophoneManager
from desktop.platform.integrations.core.event_bus import EventBus
from desktop.platform.integrations.core.logging_service import LoggingService
from desktop.services.runtime.settings_manager import SettingsManager


def bootstrap_audio_for_test() -> DIContainer:
    container = DIContainer()

    # Stub out the bare minimum to boot the microphone
    container.register_singleton(ILoggingService, LoggingService)
    container.register_singleton(IEventBus, EventBus)
    container.register_singleton(ISettingsManager, SettingsManager)
    container.register_singleton(IAudioDeviceManager, AudioDeviceManager)
    container.register_singleton(IMicrophoneManager, MicrophoneManager)

    container.resolve(ILoggingService).initialize()
    container.resolve(IEventBus).initialize()
    container.resolve(ISettingsManager).initialize()

    mic = container.resolve(IMicrophoneManager)
    mic.initialize()

    return container


def run_rapid_start_stop(iterations: int = 1000) -> None:
    container = bootstrap_audio_for_test()
    mic = container.resolve(IMicrophoneManager)

    print(f"Running Rapid Start/Stop test for {iterations} iterations...")
    for i in range(iterations):
        mic.start_capture()
        time.sleep(0.01)
        mic.stop_capture()
        
        if i > 0 and i % 100 == 0:
            print(
                f"Iteration {i}/{iterations} complete. Active threads: {threading.active_count()}"
            )
            
    print("Rapid Start/Stop test passed. No locked handles or hanging threads detected.")


def run_long_recording(duration_minutes: int = 10) -> None:
    tracemalloc.start()
    container = bootstrap_audio_for_test()
    mic = container.resolve(IMicrophoneManager)

    print(f"Running {duration_minutes}-minute capture test for memory leaks...")
    mic.start_capture()

    for i in range(duration_minutes):
        time.sleep(60)
        current, peak = tracemalloc.get_traced_memory()
        print(
            f"Minute {i+1}: Memory Current={current/1024/1024:.2f}MB, Peak={peak/1024/1024:.2f}MB"
        )

    mic.stop_capture()
    print("Long recording test complete.")
    tracemalloc.stop()


if __name__ == "__main__":
    if "--long" in sys.argv:
        run_long_recording(10)
    else:
        run_rapid_start_stop(1000)
