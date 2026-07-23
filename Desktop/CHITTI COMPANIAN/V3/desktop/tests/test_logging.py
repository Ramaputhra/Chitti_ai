import os
import shutil
import tempfile
import pytest

from desktop.platform.configuration.log_events import LogEvents
from desktop.platform.integrations.core.logging_service import LoggingService
from desktop.platform.shared.utils.performance import measure_time


@pytest.fixture
def temp_log_dir() -> str:
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_logging_service_initialization(temp_log_dir: str) -> None:
    service = LoggingService(log_dir=temp_log_dir)
    service.initialize()

    # Check files created
    assert os.path.exists(os.path.join(temp_log_dir, "debug.log"))
    assert os.path.exists(os.path.join(temp_log_dir, "application.log"))
    assert os.path.exists(os.path.join(temp_log_dir, "errors.log"))
    assert os.path.exists(os.path.join(temp_log_dir, "performance.log"))
    assert os.path.exists(os.path.join(temp_log_dir, "events.log"))
    service.shutdown()


def test_structured_event_logging(temp_log_dir: str) -> None:
    service = LoggingService(log_dir=temp_log_dir)
    service.initialize()

    service.event(LogEvents.APP_START, module="core", status="success")
    
    with open(os.path.join(temp_log_dir, "events.log"), "r") as f:
        content = f.read()
        assert "APP_START" in content
        assert "status" in content
        assert "success" in content
    service.shutdown()


def test_performance_decorator(temp_log_dir: str) -> None:
    service = LoggingService(log_dir=temp_log_dir)
    service.initialize()

    @measure_time(service, operation="Test Operation")
    def dummy_task() -> None:
        pass

    dummy_task()

    with open(os.path.join(temp_log_dir, "performance.log"), "r") as f:
        content = f.read()
        assert "Test Operation" in content
        assert "Performance: " in content
    service.shutdown()
