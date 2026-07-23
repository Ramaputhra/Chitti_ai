import os
import shutil
import tempfile
import pytest

from desktop.platform.configuration.events import SystemEvents
from desktop.services.runtime.settings_manager import SettingsManager

class MockEventBus:
    def __init__(self):
        self.published = []
    def publish(self, event):
        self.published.append(event)

class MockLogger:
    def info(self, msg, **kwargs): pass
    def exception(self, exc, **kwargs): pass

@pytest.fixture
def temp_settings_manager():
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test_settings.json")
    
    bus = MockEventBus()
    logger = MockLogger()
    manager = SettingsManager(event_bus=bus, logger=logger)
    manager._file_path = test_file
    
    yield manager, bus, test_file
    
    shutil.rmtree(temp_dir)

def test_settings_initialization(temp_settings_manager):
    manager, bus, file_path = temp_settings_manager
    manager.initialize()
    
    assert os.path.exists(file_path)
    assert manager.get("nonexistent") is None

def test_settings_read_write(temp_settings_manager):
    manager, bus, file_path = temp_settings_manager
    manager.initialize()
    
    manager.set("volume", 80)
    assert manager.get("volume") == 80
    assert manager.has("volume") is True

    # Re-initialize to ensure it writes to disk
    manager2 = SettingsManager(event_bus=bus, logger=MockLogger())
    manager2._file_path = file_path
    manager2.initialize()
    
    assert manager2.get("volume") == 80

def test_settings_publishes_event(temp_settings_manager):
    manager, bus, file_path = temp_settings_manager
    manager.initialize()
    
    manager.set("theme", "light")
    
    assert len(bus.published) == 1
    event = bus.published[0]
    assert event.id == SystemEvents.SETTINGS_CHANGED
    assert event.payload["key"] == "theme"
    assert event.payload["new_value"] == "light"
