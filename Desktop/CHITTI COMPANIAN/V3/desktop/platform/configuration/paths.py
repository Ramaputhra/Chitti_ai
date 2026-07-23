import os

# Root directories
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DESKTOP_DIR = os.path.join(ROOT_DIR, "desktop")

# Application Paths
CONFIG_DIR = os.path.join(DESKTOP_DIR, "config")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
ASSETS_DIR = os.path.join(DESKTOP_DIR, "assets")
PLUGINS_DIR = os.path.join(DESKTOP_DIR, "plugins")
STORAGE_DIR = os.path.join(DESKTOP_DIR, "storage")

# Files
DEFAULT_CONFIG_FILE = os.path.join(CONFIG_DIR, "default.yaml")
USER_SETTINGS_FILE = os.path.join(STORAGE_DIR, "settings.json")
