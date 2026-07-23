import os
import sys

class ConfigurationLoader:
    def __init__(self):
        self._config = {}
        self._is_frozen = False

    def load(self):
        self._config["ENV"] = os.getenv("CHITTI_ENV", "production")
        
        if getattr(sys, 'frozen', False):
            base_dir = os.path.join(os.environ.get("APPDATA", ""), "CHITTI_V2")
        else:
            base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            
        self._config["SQLITE_PATH"] = os.path.join(base_dir, "database", "chitti_memory.db")
        self._config["LLM_ENABLED"] = True

    def freeze(self):
        self._is_frozen = True

    def get(self, key, default=None):
        return self._config.get(key, default)
