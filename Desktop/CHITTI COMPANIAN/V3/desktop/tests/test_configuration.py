import os
import tempfile
import yaml
import pytest

from desktop.services.configuration import ConfigurationService


def test_configuration_service_hierarchy() -> None:
    # 1. Setup file config
    file_data = {"app": {"theme": "light", "port": 8080}}
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        yaml.dump(file_data, f)
        temp_path = f.name

    try:
        service = ConfigurationService()
        service.load(temp_path)

        # Test File Config
        assert service.get("app.theme") == "light"
        assert service.get("app.port") == 8080
        assert service.get("missing.key", "default") == "default"

        # Test Env Vars overriding file
        os.environ["CHITTI_APP_THEME"] = "dark"
        assert service.get("app.theme") == "dark"

        # Test Runtime Overrides overriding everything
        service.set_override("app.theme", "system")
        assert service.get("app.theme") == "system"

    finally:
        os.unlink(temp_path)
        if "CHITTI_APP_THEME" in os.environ:
            del os.environ["CHITTI_APP_THEME"]
