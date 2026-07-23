from typing import Any

from desktop.platform.integrations.core.version_manager import VersionManager


class MockLogger:
    def __init__(self) -> None:
        self.logged_messages: list[str] = []

    def info(self, msg: str, **kwargs: Any) -> None:
        self.logged_messages.append(msg)


def test_version_manager_banner() -> None:
    logger = MockLogger()
    manager = VersionManager(logger=logger)  # type: ignore
    manager.initialize()

    assert len(logger.logged_messages) == 1
    banner = logger.logged_messages[0]
    
    assert "Version:" in banner
    assert "Architecture:" in banner
    assert "Build:" in banner
    assert "Branch:" in banner


def test_version_manager_summary() -> None:
    logger = MockLogger()
    manager = VersionManager(logger=logger)  # type: ignore
    summary = manager.summary()

    assert "version" in summary
    assert "architecture" in summary
    assert "build" in summary
    assert "environment" in summary
